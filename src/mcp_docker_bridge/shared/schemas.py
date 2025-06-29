from datetime import datetime
from typing import Annotated, Any

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
    public_port: Annotated[
        int | None,
        Field(description='Public port on host')
    ] = None
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
    started_at: Annotated[
        datetime | None,
        Field(description='Container last start time (null if never started)')
    ] = None
    finished_at: Annotated[
        datetime | None,
        Field(description='Container last stop time (null if still running)')
    ] = None
    ports: Annotated[
        list[ContainerPort],
        Field(default_factory=list, description='Exposed port mappings')
    ] = []


class ListContainersFilters(BaseModel):
    """Filters for listing containers.

    Uses type-safe enums and automatic conversion to Docker API format.
    """
    exited: Annotated[
        int | None,
        Field(description='Filter by exit code')
    ] = None
    status: Annotated[
        DockerContainerState | None,
        Field(description='Filter by container status')
    ] = None
    label: Annotated[
        str | list[str] | None,
        Field(description='Filter by label(s) - string or list of strings')
    ] = None
    id: Annotated[
        str | None,
        Field(description='Filter by container ID')
    ] = None
    name: Annotated[
        str | None,
        Field(description='Filter by container name')
    ] = None
    ancestor: Annotated[
        str | None,
        Field(description='Filter by ancestor image')
    ] = None
    before: Annotated[
        str | None,
        Field(description='Only containers created before this container')
    ] = None
    since: Annotated[
        str | None,
        Field(description='Only containers created after this container')
    ] = None

    def to_docker_filters(self) -> dict[str, Any]:
        """Convert to Docker API filters format with automatic type conversion.

        Automatically handles:
        - Enum to string conversion (status.value)
        - String to list conversion for labels
        - None value exclusion
        """
        data = self.model_dump(exclude_none=True)
        filters = {}

        for field_name, field_value in data.items():
            try:
                docker_key = DockerContainerFilterKey(field_name)
            except ValueError:
                continue

            if field_name == 'status' and hasattr(field_value, 'value'):
                filters[docker_key] = field_value.value
            elif field_name == 'label':
                filters[docker_key] = (
                    field_value if isinstance(field_value, list)
                    else [field_value]
                )
            else:
                filters[docker_key] = field_value

        return filters


class ListContainersParams(BaseModel):
    """Parameters for listing containers.
    """
    all: Annotated[
        bool,
        Field(description='Show all containers (default shows just running)')
    ] = False

    since: Annotated[
        str | None,
        Field(description='Show only containers created since Id or Name')
    ] = None

    before: Annotated[
        str | None,
        Field(description='Show only containers created before Id or Name')
    ] = None

    limit: Annotated[
        int | None,
        Field(description='Show limit last created containers')
    ] = None

    filters: Annotated[
        ListContainersFilters | None,
        Field(description='Filters to apply')
    ] = None

    sparse: Annotated[
        bool,
        Field(description='Do not inspect containers for full details')
    ] = False

    ignore_removed: Annotated[
        bool,
        Field(description='Ignore failures due to missing containers')
    ] = False

    def model_dump_docker_api(self) -> dict[str, Any]:
        """Get parameters ready for Docker API client.containers.list().

        Returns dict with non-None values and filters converted to Docker
        format.
        """
        data = self.model_dump(exclude_none=True)

        if 'filters' in data and self.filters is not None:
            data['filters'] = self.filters.to_docker_filters()

        return data


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
