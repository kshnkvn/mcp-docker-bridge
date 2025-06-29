from datetime import UTC, datetime
from typing import Any

import docker
from docker import DockerClient
from docker.errors import DockerException
from loguru import logger

from mcp_docker_bridge.shared.constants import (
    DockerContainerAttrKey,
    DockerContainerListAPIParam,
    DockerContainerPortAttrKey,
    DockerContainerStateAttrKey,
    DockerPortType,
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
        kwargs = self._build_list_kwargs(
            all, since, before, limit, filters, sparse, ignore_removed
        )
        containers = self.client.containers.list(**kwargs)

        container_infos = []
        for container in containers:
            container_data = self._extract_container_data(container)
            container_infos.append(self._convert_container_data(container_data))

        return container_infos

    def _build_list_kwargs(
        self,
        all: bool,
        since: str | None,
        before: str | None,
        limit: int | None,
        filters: dict[str, Any] | None,
        sparse: bool,
        ignore_removed: bool,
    ) -> dict[str, Any]:
        """Build kwargs dictionary for Docker API using StrEnum values.
        """
        params = {
            DockerContainerListAPIParam.ALL: all,
            DockerContainerListAPIParam.SINCE: since,
            DockerContainerListAPIParam.BEFORE: before,
            DockerContainerListAPIParam.LIMIT: limit,
            DockerContainerListAPIParam.FILTERS: filters,
            DockerContainerListAPIParam.SPARSE: sparse,
            DockerContainerListAPIParam.IGNORE_REMOVED: ignore_removed,
        }

        return {
            key: value for key, value in params.items()
            if value is not None and (not isinstance(value, bool) or value)
        }

    def _extract_container_data(self, container) -> dict[str, Any]:
        """Extract container data from Docker container object.
        """
        container_names = []
        if hasattr(container, 'name') and container.name:
            container_names = [container.name]

        return {
            'id': container.id,
            DockerContainerAttrKey.NAMES: container_names,
            DockerContainerAttrKey.IMAGE: container.attrs.get(
                DockerContainerAttrKey.IMAGE, ''
            ),
            DockerContainerAttrKey.CREATED: container.attrs.get(
                DockerContainerAttrKey.CREATED, 0
            ),
            DockerContainerAttrKey.PORTS: container.attrs.get(
                DockerContainerAttrKey.PORTS, []
            ),
            DockerContainerAttrKey.STATE: container.attrs.get(
                DockerContainerAttrKey.STATE, {}
            ),
        }

    def _convert_container_data(
        self,
        container_data: dict[str, Any],
    ) -> ContainerInfo:
        """Convert raw Docker API container data to ContainerInfo model.
        """
        ports_data = container_data.get(DockerContainerAttrKey.PORTS, [])
        ports = self._parse_ports(ports_data)
        state_data = container_data.get(DockerContainerAttrKey.STATE, {})
        state_string = self._extract_state_string(state_data)

        created_at = self._parse_datetime_value(
            container_data.get(DockerContainerAttrKey.CREATED, 0)
        )
        started_at = self._parse_state_datetime(
            state_data, DockerContainerStateAttrKey.STARTED_AT
        )
        finished_at = self._parse_state_datetime(
            state_data, DockerContainerStateAttrKey.FINISHED_AT
        )

        return ContainerInfo(
            id=container_data['id'],
            names=container_data.get(DockerContainerAttrKey.NAMES, []),
            image=container_data.get(DockerContainerAttrKey.IMAGE, ''),
            state=state_string,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            ports=ports,
        )

    def _parse_ports(
        self, ports_data: list[dict[str, Any]]
    ) -> list[ContainerPort]:
        """Parse port data into ContainerPort objects.
        """
        ports = []
        for port_data in ports_data:
            private_port_key = DockerContainerPortAttrKey.PRIVATE_PORT
            public_port_key = DockerContainerPortAttrKey.PUBLIC_PORT
            type_key = DockerContainerPortAttrKey.TYPE

            port = ContainerPort(
                private_port=port_data.get(private_port_key, 0),
                public_port=port_data.get(public_port_key),
                type=DockerPortType(
                    port_data.get(type_key, DockerPortType.TCP)
                ),
            )
            ports.append(port)
        return ports

    def _extract_state_string(self, state_data: dict[str, Any] | Any) -> str:
        """Extract state string from State dictionary.
        """
        if isinstance(state_data, dict):
            return state_data.get(DockerContainerStateAttrKey.STATUS, '')
        return str(state_data) if state_data else ''

    def _parse_state_datetime(
        self,
        state_data: dict[str, Any],
        key: DockerContainerStateAttrKey
    ) -> datetime | None:
        """Parse datetime from state data for given key.
        """
        if not isinstance(state_data, dict):
            return None

        datetime_value = state_data.get(key)
        if datetime_value:
            return self._parse_datetime_value(datetime_value)
        return None

    def _parse_datetime_value(self, value: Any) -> datetime:
        """Parse datetime value from various formats (string, timestamp, etc.).

        Returns timezone-aware datetime or current UTC time as fallback.
        """
        if isinstance(value, str):
            return self._parse_iso_datetime(value)

        if isinstance(value, int | float) and value > 0:
            return datetime.fromtimestamp(value, UTC)

        return datetime.now(UTC)

    def _parse_iso_datetime(self, iso_string: str) -> datetime:
        """Parse ISO 8601 datetime string to timezone-aware datetime.
        """
        try:
            if iso_string.endswith('Z'):
                # Replace Z with explicit UTC offset
                return datetime.fromisoformat(
                    iso_string.rstrip('Z') + '+00:00'
                )

            parsed_dt = datetime.fromisoformat(iso_string)
            # If naive datetime, assume UTC
            if parsed_dt.tzinfo is None:
                return parsed_dt.replace(tzinfo=UTC)
            return parsed_dt

        except ValueError:
            # Fallback if parsing fails
            return datetime.now(UTC)
