from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from mcp_docker_bridge.shared.constants import (
    DockerContainerFilterKey,
    DockerContainerState,
    DockerPortType,
)


class ContainerPort(BaseModel):
    """Container port mapping information.
    """
    private_port: int = Field(..., description='Private port inside container')
    public_port: int | None = Field(None, description='Public port on host')
    type: DockerPortType = Field(..., description='Port type (tcp/udp)')


class ContainerInfo(BaseModel):
    """Container information returned by list_containers.

    This is a simplified view suitable for listing containers.
    For detailed container information, use a dedicated inspection tool.
    """
    id: str = Field(..., description='Container ID')
    names: list[str] = Field(..., description='Container names')
    image: str = Field(..., description='Image name')
    state: str = Field(
        ..., description='Container state (running, exited, etc.)'
    )
    created_at: datetime = Field(..., description='Container creation time')
    started_at: datetime | None = Field(
        None, description='Container last start time (null if never started)'
    )
    finished_at: datetime | None = Field(
        None, description='Container last stop time (null if still running)'
    )
    ports: list[ContainerPort] = Field(
        default_factory=list,
        description='Exposed port mappings',
    )


class ListContainersFilters(BaseModel):
    """Filters for listing containers.
    """
    exited: int | None = Field(None, description='Filter by exit code')
    status: DockerContainerState | None = Field(
        None,
        description='Filter by container status',
    )
    label: str | list[str] | None = Field(None, description='Filter by label')
    id: str | None = Field(None, description='Filter by container ID')
    name: str | None = Field(None, description='Filter by container name')
    ancestor: str | None = Field(None, description='Filter by ancestor image')
    before: str | None = Field(
        None,
        description='Only containers created before this container',
    )
    since: str | None = Field(
        None,
        description='Only containers created after this container',
    )

    def to_docker_filters(self) -> dict[str, Any]:
        """Convert to Docker API filters format.
        """
        filters = {}

        if self.exited is not None:
            filters[DockerContainerFilterKey.EXITED] = self.exited

        if self.status is not None:
            filters[DockerContainerFilterKey.STATUS] = self.status.value

        if self.label is not None:
            filters[DockerContainerFilterKey.LABEL] = (
                self.label if isinstance(self.label, list) else [self.label]
            )

        if self.id is not None:
            filters[DockerContainerFilterKey.ID] = self.id

        if self.name is not None:
            filters[DockerContainerFilterKey.NAME] = self.name

        if self.ancestor is not None:
            filters[DockerContainerFilterKey.ANCESTOR] = self.ancestor

        if self.before is not None:
            filters[DockerContainerFilterKey.BEFORE] = self.before

        if self.since is not None:
            filters[DockerContainerFilterKey.SINCE] = self.since

        return filters


class ListContainersParams(BaseModel):
    """Parameters for listing containers.
    """
    all: bool = Field(
        False,
        description='Show all containers (default shows just running)',
    )
    since: str | None = Field(
        None,
        description='Show only containers created since Id or Name',
    )
    before: str | None = Field(
        None,
        description='Show only containers created before Id or Name',
    )
    limit: int | None = Field(
        None,
        description='Show limit last created containers',
    )
    filters: ListContainersFilters | None = Field(
        None,
        description='Filters to apply',
    )
    sparse: bool = Field(
        False,
        description='Do not inspect containers for full details',
    )
    ignore_removed: bool = Field(
        False,
        description='Ignore failures due to missing containers',
    )


class ListContainersResponse(BaseModel):
    """Response from list_containers tool.
    """
    containers: list[ContainerInfo] = Field(
        ...,
        description='List of containers',
    )
    total_count: int = Field(
        ...,
        description='Total number of containers returned',
    )
