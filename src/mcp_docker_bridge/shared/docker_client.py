from datetime import UTC, datetime
from typing import Any

import docker
from docker import DockerClient
from docker.errors import DockerException
from loguru import logger

from mcp_docker_bridge.shared.constants import (
    ContainerAttrKey,
    DockerAPIParam,
    PortAttrKey,
    PortType,
    StateAttrKey,
)
from mcp_docker_bridge.shared.schemas import (
    ContainerInfo,
    ContainerPort,
)


class DockerClientManager:
    def __init__(self) -> None:
        """Initialize the Docker client manager.
        """
        self._client: DockerClient | None = None

    def connect(self) -> None:
        """Establish connection to Docker daemon.
        """
        if self._client is not None:
            return

        try:
            self._client = docker.from_env()
            self._client.ping()
            logger.info('Successfully connected to Docker daemon')
        except DockerException as e:
            logger.error(f'Failed to connect to Docker daemon: {e}')
            raise

    def disconnect(self) -> None:
        """Close connection to Docker daemon.
        """
        if self._client is not None:
            try:
                self._client.close()
                logger.info('Disconnected from Docker daemon')
            except Exception as e:
                logger.error(f'Error closing Docker client: {e}')
            finally:
                self._client = None

    @property
    def client(self) -> DockerClient:
        """Get the Docker client instance.
        """
        if self._client is None:
            raise RuntimeError(
                'Docker client is not connected. Call connect() first.'
            )
        return self._client

    def list_containers(
        self,
        all: bool = False,
        since: str | None = None,
        before: str | None = None,
        limit: int | None = None,
        filters: dict[str, Any] | None = None,
        sparse: bool = False,
        ignore_removed: bool = False,
    ) -> list['ContainerInfo']:
        """List containers using Docker API and return ContainerInfo objects.

        Args:
            all: Show all containers (default shows just running)
            since: Show only containers created since Id or Name
            before: Show only containers created before Id or Name
            limit: Show limit last created containers
            filters: Filters to apply
            sparse: Do not inspect containers for full details
            ignore_removed: Ignore failures due to missing containers

        Returns:
            List of ContainerInfo objects
        """
        # Build kwargs using StrEnum values
        kwargs = {}

        if all:
            kwargs[DockerAPIParam.ALL] = all
        if since is not None:
            kwargs[DockerAPIParam.SINCE] = since
        if before is not None:
            kwargs[DockerAPIParam.BEFORE] = before
        if limit is not None:
            kwargs[DockerAPIParam.LIMIT] = limit
        if filters is not None:
            kwargs[DockerAPIParam.FILTERS] = filters
        if sparse:
            kwargs[DockerAPIParam.SPARSE] = sparse
        if ignore_removed:
            kwargs[DockerAPIParam.IGNORE_REMOVED] = ignore_removed

        containers = self.client.containers.list(**kwargs)

        # Convert Container objects to dictionaries, then to ContainerInfo
        container_infos = []
        for container in containers:
            # Extract container name and convert to array format
            container_names = []
            if hasattr(container, 'name') and container.name:
                container_names = [container.name]

            data = {
                'id': container.id,
                ContainerAttrKey.NAMES: container_names,
                ContainerAttrKey.IMAGE: container.attrs.get(
                    ContainerAttrKey.IMAGE, ''
                ),
                ContainerAttrKey.CREATED: container.attrs.get(
                    ContainerAttrKey.CREATED, 0
                ),
                ContainerAttrKey.PORTS: container.attrs.get(
                    ContainerAttrKey.PORTS, []
                ),
                ContainerAttrKey.STATE: container.attrs.get(
                    ContainerAttrKey.STATE, {}
                ),
            }

            container_infos.append(self._convert_container_data(data))

        return container_infos

    def _convert_container_data(
        self,
        container_data: dict[str, Any],
    ) -> ContainerInfo:
        """Convert raw Docker API container data to ContainerInfo model.
        """
        # Parse ports (simplified)
        ports = []
        for port_data in container_data.get(ContainerAttrKey.PORTS, []):
            port = ContainerPort(
                private_port=port_data.get(PortAttrKey.PRIVATE_PORT, 0),
                public_port=port_data.get(PortAttrKey.PUBLIC_PORT),
                type=PortType(port_data.get(PortAttrKey.TYPE, PortType.TCP)),
            )
            ports.append(port)

        # Parse state - extract state string from State dictionary
        state_data = container_data.get(ContainerAttrKey.STATE, {})
        if isinstance(state_data, dict):
            state_string = state_data.get(StateAttrKey.STATUS, '')
        else:
            state_string = str(state_data) if state_data else ''

        # Extract started_at from State.StartedAt
        started_at = None
        if isinstance(state_data, dict):
            started_at_value = state_data.get(StateAttrKey.STARTED_AT)
            if started_at_value:
                # Handle different datetime formats
                if isinstance(started_at_value, str):
                    try:
                        if started_at_value.endswith('Z'):
                            started_at = datetime.fromisoformat(
                                started_at_value.rstrip('Z') + '+00:00'
                            )
                        else:
                            started_at = datetime.fromisoformat(
                                started_at_value
                            )
                            if started_at.tzinfo is None:
                                started_at = started_at.replace(tzinfo=UTC)
                    except ValueError:
                        # If parsing fails, leave as None
                        pass
                elif (
                    isinstance(started_at_value, int | float)
                    and started_at_value > 0
                ):
                    started_at = datetime.fromtimestamp(started_at_value, UTC)

        # Extract finished_at from State.FinishedAt
        finished_at = None
        if isinstance(state_data, dict):
            finished_at_value = state_data.get(StateAttrKey.FINISHED_AT)
            if finished_at_value:
                # Handle different datetime formats
                if isinstance(finished_at_value, str):
                    try:
                        if finished_at_value.endswith('Z'):
                            finished_at = datetime.fromisoformat(
                                finished_at_value.rstrip('Z') + '+00:00'
                            )
                        else:
                            finished_at = datetime.fromisoformat(
                                finished_at_value
                            )
                            if finished_at.tzinfo is None:
                                finished_at = finished_at.replace(tzinfo=UTC)
                    except ValueError:
                        # If parsing fails, leave as None
                        pass
                elif (
                    isinstance(finished_at_value, int | float)
                    and finished_at_value > 0
                ):
                    finished_at = datetime.fromtimestamp(
                        finished_at_value, UTC
                    )

        # Convert timestamp to datetime
        created_value = container_data.get(ContainerAttrKey.CREATED, 0)

        # Handle both string (ISO format) and integer (Unix timestamp) formats
        if isinstance(created_value, str):
            try:
                # Parse ISO 8601 format, ensure timezone-aware
                if created_value.endswith('Z'):
                    # Replace Z with explicit UTC offset
                    created_at = datetime.fromisoformat(
                        created_value.rstrip('Z') + '+00:00'
                    )
                else:
                    created_at = datetime.fromisoformat(created_value)
                    # If naive datetime, assume UTC
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=UTC)
            except ValueError:
                # Fallback if parsing fails - use UTC
                created_at = datetime.now(UTC)
        elif isinstance(created_value, int | float) and created_value > 0:
            # Create timezone-aware datetime from timestamp (UTC)
            created_at = datetime.fromtimestamp(created_value, UTC)
        else:
            # Default fallback - use UTC
            created_at = datetime.now(UTC)

        return ContainerInfo(
            id=container_data['id'],
            names=container_data.get(ContainerAttrKey.NAMES, []),
            image=container_data.get(ContainerAttrKey.IMAGE, ''),
            state=state_string,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            ports=ports,
        )
