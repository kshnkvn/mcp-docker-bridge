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
        Field(description='Public port on host'),
    ] = None
    type: DockerPortType = Field(..., description='Port type (tcp/udp)')
    ip: Annotated[
        str | None,
        Field(description='IP address for port binding'),
    ] = None


class ContainerInfo(BaseModel):
    """Container information returned by list_containers.

    This is a simplified view suitable for listing containers.
    For detailed container information, use a dedicated inspection tool.
    """
    id: str = Field(..., description='Container ID')
    names: list[str] = Field(..., description='Container names')
    image: str = Field(..., description='Image name')
    state: str = Field(
        ...,
        description='Container state (running, exited, etc.)',
    )
    created_at: datetime = Field(..., description='Container creation time')
    started_at: Annotated[
        datetime | None,
        Field(description='Container last start time (null if never started)'),
    ] = None
    finished_at: Annotated[
        datetime | None,
        Field(description='Container last stop time (null if still running)'),
    ] = None
    ports: Annotated[
        list[ContainerPort],
        Field(default_factory=list, description='Exposed port mappings'),
    ] = []


class ListContainersFilters(BaseModel):
    """Filters for listing containers.

    Uses type-safe enums and automatic conversion to Docker API format.
    """
    exited: Annotated[
        int | None,
        Field(description='Filter by exit code'),
    ] = None
    status: Annotated[
        DockerContainerState | None,
        Field(description='Filter by container status'),
    ] = None
    label: Annotated[
        str | list[str] | None,
        Field(description='Filter by label(s) - string or list of strings'),
    ] = None
    id: Annotated[
        str | None,
        Field(description='Filter by container ID'),
    ] = None
    name: Annotated[
        str | None,
        Field(description='Filter by container name'),
    ] = None
    ancestor: Annotated[
        str | None,
        Field(description='Filter by ancestor image'),
    ] = None
    before: Annotated[
        str | None,
        Field(description='Only containers created before this container'),
    ] = None
    since: Annotated[
        str | None,
        Field(description='Only containers created after this container'),
    ] = None

    def to_docker_filters(self) -> dict[str, Any]:
        """Convert to Docker API filters format with automatic type conversion.

        Automatically handles:
        - Enum to string conversion (status.value)
        - String to list conversion for labels
        - None value exclusion
        """
        data = self.model_dump(exclude_none=True)
        filters: dict[str, Any] = {}

        for field_name, field_value in data.items():
            try:
                docker_key = DockerContainerFilterKey(field_name)
            except ValueError:
                continue

            if field_name == 'status' and hasattr(field_value, 'value'):
                filters[str(docker_key)] = field_value.value
            elif field_name == 'label':
                filters[str(docker_key)] = (
                    field_value if isinstance(field_value, list)
                    else [field_value]
                )
            else:
                filters[str(docker_key)] = field_value

        return filters


class ListContainersParams(BaseModel):
    """Parameters for listing containers.
    """
    all: Annotated[
        bool,
        Field(description='Show all containers (default shows just running)'),
    ] = False

    since: Annotated[
        str | None,
        Field(description='Show only containers created since Id or Name'),
    ] = None

    before: Annotated[
        str | None,
        Field(description='Show only containers created before Id or Name'),
    ] = None

    limit: Annotated[
        int | None,
        Field(description='Show limit last created containers'),
    ] = None

    filters: Annotated[
        ListContainersFilters | None,
        Field(description='Filters to apply'),
    ] = None

    sparse: Annotated[
        bool,
        Field(description='Do not inspect containers for full details'),
    ] = False

    ignore_removed: Annotated[
        bool,
        Field(description='Ignore failures due to missing containers'),
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


class GetContainerParams(BaseModel):
    """Parameters for getting container details.
    """
    container_id: str = Field(
        ...,
        description='Container ID (full or short) or container name',
        min_length=1,
    )
    use_cache: bool = Field(
        default=True,
        description='Whether to use cached data if available',
    )


class RestartPolicy(BaseModel):
    """Container restart policy configuration.
    """
    name: str = 'no'  # no, always, on-failure, unless-stopped
    maximum_retry_count: int = 0


class Mount(BaseModel):
    """Container mount point information.
    """
    type: str  # bind, volume, tmpfs
    source: str
    destination: str
    mode: str = 'rw'  # rw, ro
    rw: bool = True
    propagation: str = 'rprivate'


class NetworkEndpoint(BaseModel):
    """Network endpoint configuration.
    """
    network_id: str
    endpoint_id: str
    gateway: str | None = None
    ip_address: str | None = None
    ip_prefix_len: int | None = None
    ipv6_gateway: str | None = None
    global_ipv6_address: str | None = None
    global_ipv6_prefix_len: int | None = None
    mac_address: str | None = None


class HealthCheck(BaseModel):
    """Container health check configuration.
    """
    test: list[str] | None = None
    interval: int | None = None  # nanoseconds
    timeout: int | None = None   # nanoseconds
    retries: int | None = None
    start_period: int | None = None  # nanoseconds


class ResourceLimits(BaseModel):
    """Container resource limits.
    """
    cpu_shares: int | None = None
    cpu_period: int | None = None
    cpu_quota: int | None = None
    cpuset_cpus: str | None = None
    cpuset_mems: str | None = None
    memory: int | None = None
    memory_swap: int | None = None
    memory_reservation: int | None = None
    kernel_memory: int | None = None
    blkio_weight: int | None = None
    pids_limit: int | None = None


class DetailedContainerInfo(ContainerInfo):
    """Comprehensive container information including all configuration details.

    Extends ContainerInfo with additional fields needed for container
    recreation.
    """
    # Additional identification
    image_id: str
    status: str

    # Detailed configuration
    entrypoint: list[str] | None = None
    cmd: list[str] | None = None
    working_dir: str | None = None
    user: str | None = None
    hostname: str | None = None
    domainname: str | None = None
    env: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)

    # Runtime state (extending base timestamps)
    exit_code: int | None = None
    error: str | None = None
    running: bool = False
    paused: bool = False
    restarting: bool = False
    pid: int | None = None

    # Networking (extending base ports)
    network_mode: str = 'default'
    exposed_ports: dict[str, dict] = Field(default_factory=dict)
    networks: dict[str, NetworkEndpoint] = Field(default_factory=dict)

    # Storage
    mounts: list[Mount] = Field(default_factory=list)
    volumes: dict[str, dict] = Field(default_factory=dict)

    # Resources and policies
    restart_policy: RestartPolicy = Field(default_factory=RestartPolicy)
    resources: ResourceLimits = Field(default_factory=ResourceLimits)
    privileged: bool = False
    cap_add: list[str] = Field(default_factory=list)
    cap_drop: list[str] = Field(default_factory=list)

    # Health and logging
    health_check: HealthCheck | None = None
    log_config: dict[str, Any] = Field(default_factory=dict)

    # Additional settings
    tty: bool = False
    stdin_open: bool = False
    extra_hosts: list[str] = Field(default_factory=list)
    group_add: list[str] = Field(default_factory=list)
    security_opt: list[str] = Field(default_factory=list)

    def to_create_params(self) -> dict[str, Any]:
        """Convert to parameters suitable for container creation.
        """
        params = {
            'image': self.image,
            'command': self.cmd,
            'entrypoint': self.entrypoint,
            'working_dir': self.working_dir,
            'user': self.user,
            'hostname': self.hostname,
            'domainname': self.domainname,
            'environment': self.env,
            'labels': self.labels,
            'ports': self.exposed_ports,
            'volumes': self.volumes,
            'tty': self.tty,
            'stdin_open': self.stdin_open,
        }

        # Host config parameters
        host_config: dict[str, Any] = {
            'binds': [
                f"{m.source}:{m.destination}:{m.mode}"
                for m in self.mounts if m.type == 'bind'
            ],
            'port_bindings': self._create_port_bindings(),
            'restart_policy': {
                'Name': self.restart_policy.name,
                'MaximumRetryCount': self.restart_policy.maximum_retry_count
            },
            'network_mode': self.network_mode,
            'privileged': self.privileged,
            'cap_add': self.cap_add or None,
            'cap_drop': self.cap_drop or None,
            'extra_hosts': self.extra_hosts or None,
            'group_add': self.group_add or None,
            'security_opt': self.security_opt or None,
            'log_config': self.log_config or None,
        }

        # Add resource limits if any are set
        if any(
            getattr(self.resources, field) is not None
            for field in self.resources.model_fields
        ):
            host_config.update({
                'cpu_shares': self.resources.cpu_shares,
                'cpu_period': self.resources.cpu_period,
                'cpu_quota': self.resources.cpu_quota,
                'cpuset_cpus': self.resources.cpuset_cpus,
                'cpuset_mems': self.resources.cpuset_mems,
                'mem_limit': self.resources.memory,
                'memswap_limit': self.resources.memory_swap,
                'mem_reservation': self.resources.memory_reservation,
            })

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        host_config = {k: v for k, v in host_config.items() if v is not None}

        if host_config:
            params['host_config'] = host_config

        return params

    def _create_port_bindings(
        self
    ) -> dict[str, list[dict[str, Any]]] | None:
        """Create port bindings dictionary from ports list.
        """
        if not self.ports:
            return None

        bindings: dict[str, list[dict[str, Any]]] = {}
        for port in self.ports:
            if port.public_port:
                key = f"{port.private_port}/{port.type}"
                binding: dict[str, Any] = {'HostPort': str(port.public_port)}
                if port.ip:
                    binding['HostIp'] = port.ip
                if key not in bindings:
                    bindings[key] = []
                bindings[key].append(binding)

        return bindings if bindings else None
