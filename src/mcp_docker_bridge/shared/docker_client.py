from datetime import UTC, datetime
from typing import Any

import docker
from docker import DockerClient
from docker import errors as docker_errors
from docker.errors import DockerException
from loguru import logger

from mcp_docker_bridge.shared.constants import (
    DockerConfigAttrKey,
    DockerContainerAttrKey,
    DockerContainerPortAttrKey,
    DockerContainerStateAttrKey,
    DockerHealthCheckAttrKey,
    DockerHostConfigAttrKey,
    DockerMountAttrKey,
    DockerNetworkAttrKey,
    DockerPortType,
    DockerRestartPolicyAttrKey,
    DockerTopLevelAttrKey,
)
from mcp_docker_bridge.shared.schemas import (
    ContainerInfo,
    ContainerPort,
    DetailedContainerInfo,
    HealthCheck,
    ListContainersParams,
    Mount,
    NetworkEndpoint,
    ResourceLimits,
    RestartPolicy,
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

    def _is_connected(self) -> bool:
        """Check if Docker client is connected.
        """
        return self._client is not None

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
        params: ListContainersParams | None = None,
    ) -> list['ContainerInfo']:
        """List containers using Docker API and return ContainerInfo objects.

        Args:
            params: Container listing parameters. If None, uses defaults.

        Returns:
            List of ContainerInfo objects
        """
        if params is None:
            params = ListContainersParams()

        kwargs = params.model_dump_docker_api()
        containers = self.client.containers.list(**kwargs)

        container_infos = []
        for container in containers:
            container_data = self._extract_container_data(container)
            container_infos.append(self._convert_container_data(container_data))

        return container_infos

    def _extract_container_data(self, container) -> dict[str, Any]:
        """Extract container data from Docker container object.
        """
        container_names = []
        if hasattr(container, 'name') and container.name:
            container_names = [container.name]

        return {
            DockerContainerAttrKey.ID: container.id,
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
            id=container_data[DockerContainerAttrKey.ID],
            names=container_data.get(DockerContainerAttrKey.NAMES, []),
            image=container_data.get(DockerContainerAttrKey.IMAGE, ''),
            state=state_string,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
            ports=ports,
        )

    def _parse_ports(
        self,
        ports_data: list[dict[str, Any]],
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
                ip=port_data.get(DockerContainerPortAttrKey.IP),
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
        key: DockerContainerStateAttrKey,
    ) -> datetime | None:
        """Parse datetime from state data for given key.
        """
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

    def get_container(self, container_id: str) -> DetailedContainerInfo:
        """Get detailed information about a specific container.

        Args:
            container_id: Container ID or name

        Returns:
            Detailed container information

        Raises:
            RuntimeError: If not connected or container not found
        """
        if not self._is_connected():
            raise RuntimeError('Docker client is not connected')

        try:
            container = self.client.containers.get(container_id)
            attrs = container.attrs

            # Extract configuration data using enum constants
            config = attrs.get(DockerTopLevelAttrKey.CONFIG, {})
            host_config = attrs.get(DockerTopLevelAttrKey.HOST_CONFIG, {})
            state = attrs.get(DockerTopLevelAttrKey.STATE, {})
            network_settings = attrs.get(
                DockerTopLevelAttrKey.NETWORK_SETTINGS, {}
            )

            # Reuse existing _extract_container_data for basic info
            basic_data = self._extract_container_data(container)

            # Build detailed container info
            container_info = DetailedContainerInfo(
                # Basic info from existing method
                id=basic_data[DockerContainerAttrKey.ID],
                names=basic_data.get(DockerContainerAttrKey.NAMES, []),
                image=basic_data.get(DockerContainerAttrKey.IMAGE, ''),
                created_at=self._parse_datetime_value(
                    basic_data.get(DockerContainerAttrKey.CREATED)
                ),
                state=self._extract_state_string(state),
                started_at=self._parse_datetime_value(
                    state.get(DockerContainerStateAttrKey.STARTED_AT)
                ),
                finished_at=self._parse_datetime_value(
                    state.get(DockerContainerStateAttrKey.FINISHED_AT)
                ),
                ports=self._parse_ports(
                    basic_data.get(DockerContainerAttrKey.PORTS, [])
                ),

                # Additional identification
                image_id=attrs.get(DockerTopLevelAttrKey.IMAGE, ''),
                status=state.get(
                    DockerContainerStateAttrKey.STATUS, 'unknown'
                ),

                # Configuration
                entrypoint=config.get(DockerConfigAttrKey.ENTRYPOINT),
                cmd=config.get(DockerConfigAttrKey.CMD),
                working_dir=config.get(DockerConfigAttrKey.WORKING_DIR),
                user=config.get(DockerConfigAttrKey.USER),
                hostname=config.get(DockerConfigAttrKey.HOSTNAME),
                domainname=config.get(DockerConfigAttrKey.DOMAINNAME),
                env=config.get(DockerConfigAttrKey.ENV, []),
                labels=config.get(DockerConfigAttrKey.LABELS, {}),

                # Runtime state
                exit_code=state.get(DockerContainerStateAttrKey.EXIT_CODE),
                error=state.get(DockerContainerStateAttrKey.ERROR) or None,
                running=state.get(DockerContainerStateAttrKey.RUNNING, False),
                paused=state.get(DockerContainerStateAttrKey.PAUSED, False),
                restarting=state.get(
                    DockerContainerStateAttrKey.RESTARTING, False
                ),
                pid=state.get(DockerContainerStateAttrKey.PID),

                # Networking
                network_mode=host_config.get(
                    DockerHostConfigAttrKey.NETWORK_MODE, 'default'
                ),
                exposed_ports=config.get(
                    DockerConfigAttrKey.EXPOSED_PORTS, {}
                ),
                networks=self._parse_networks(
                    network_settings.get(DockerContainerAttrKey.NETWORKS, {})
                ),

                # Storage
                mounts=self._parse_mounts(
                    attrs.get(DockerTopLevelAttrKey.MOUNTS, [])
                ),
                volumes=config.get(DockerConfigAttrKey.VOLUMES, {}),

                # Resources and policies
                restart_policy=self._parse_restart_policy(
                    host_config.get(DockerHostConfigAttrKey.RESTART_POLICY, {})
                ),
                resources=self._parse_resources(host_config),
                privileged=host_config.get(
                    DockerHostConfigAttrKey.PRIVILEGED, False
                ),
                cap_add=host_config.get(
                    DockerHostConfigAttrKey.CAP_ADD
                ) or [],
                cap_drop=host_config.get(
                    DockerHostConfigAttrKey.CAP_DROP
                ) or [],

                # Health and logging
                health_check=self._parse_health_check(
                    config.get(DockerConfigAttrKey.HEALTHCHECK)
                ),
                log_config=host_config.get(
                    DockerHostConfigAttrKey.LOG_CONFIG, {}
                ),

                # Additional settings
                tty=config.get(DockerConfigAttrKey.TTY, False),
                stdin_open=config.get(DockerConfigAttrKey.OPEN_STDIN, False),
                extra_hosts=host_config.get(
                    DockerHostConfigAttrKey.EXTRA_HOSTS
                ) or [],
                group_add=host_config.get(
                    DockerHostConfigAttrKey.GROUP_ADD
                ) or [],
                security_opt=host_config.get(
                    DockerHostConfigAttrKey.SECURITY_OPT
                ) or [],
            )

            return container_info

        except docker_errors.NotFound:
            raise RuntimeError(f'Container not found: {container_id}')
        except Exception as e:
            logger.error(f'Failed to get container {container_id}: {e}')
            raise RuntimeError(f'Failed to get container information: {e}')

    def _parse_networks(
        self,
        networks: dict[str, Any],
    ) -> dict[str, NetworkEndpoint]:
        """Parse network settings into NetworkEndpoint objects.
        """
        result = {}
        for name, data in networks.items():
            if isinstance(data, dict):
                result[name] = NetworkEndpoint(
                    network_id=data.get(DockerNetworkAttrKey.NETWORK_ID, ''),
                    endpoint_id=data.get(DockerNetworkAttrKey.ENDPOINT_ID, ''),
                    gateway=data.get(DockerNetworkAttrKey.GATEWAY),
                    ip_address=data.get(
                        DockerNetworkAttrKey.IP_ADDRESS
                    ),
                    ip_prefix_len=data.get(
                        DockerNetworkAttrKey.IP_PREFIX_LEN
                    ),
                    ipv6_gateway=data.get(
                        DockerNetworkAttrKey.IPV6_GATEWAY
                    ),
                    global_ipv6_address=data.get(
                        DockerNetworkAttrKey.GLOBAL_IPV6_ADDRESS
                    ),
                    global_ipv6_prefix_len=data.get(
                        DockerNetworkAttrKey.GLOBAL_IPV6_PREFIX_LEN
                    ),
                    mac_address=data.get(
                        DockerNetworkAttrKey.MAC_ADDRESS
                    ),
                )
        return result

    def _parse_mounts(
        self,
        mounts: list[dict[str, Any]],
    ) -> list[Mount]:
        """Parse mount information into Mount objects.
        """
        result = []
        for mount in mounts:
            if isinstance(mount, dict):
                result.append(Mount(
                    type=mount.get(DockerMountAttrKey.TYPE, 'bind'),
                    source=mount.get(
                        DockerMountAttrKey.SOURCE, ''
                    ),
                    destination=mount.get(
                        DockerMountAttrKey.DESTINATION, ''
                    ),
                    mode=mount.get(DockerMountAttrKey.MODE, 'rw'),
                    rw=mount.get(DockerMountAttrKey.RW, True),
                    propagation=mount.get(
                        DockerMountAttrKey.PROPAGATION, 'rprivate'
                    ),
                ))
        return result

    def _parse_restart_policy(
        self,
        policy: dict[str, Any],
    ) -> RestartPolicy:
        """Parse restart policy configuration.
        """
        return RestartPolicy(
            name=policy.get(
                DockerRestartPolicyAttrKey.NAME, 'no'
            ),
            maximum_retry_count=policy.get(
                DockerRestartPolicyAttrKey.MAXIMUM_RETRY_COUNT, 0
            ),
        )

    def _parse_resources(
        self,
        host_config: dict[str, Any],
    ) -> ResourceLimits:
        """Parse resource limits from host configuration.
        """
        return ResourceLimits(
            cpu_shares=host_config.get(
                DockerHostConfigAttrKey.CPU_SHARES
            ),
            cpu_period=host_config.get(
                DockerHostConfigAttrKey.CPU_PERIOD
            ),
            cpu_quota=host_config.get(
                DockerHostConfigAttrKey.CPU_QUOTA
            ),
            cpuset_cpus=host_config.get(
                DockerHostConfigAttrKey.CPUSET_CPUS
            ),
            cpuset_mems=host_config.get(
                DockerHostConfigAttrKey.CPUSET_MEMS
            ),
            memory=host_config.get(
                DockerHostConfigAttrKey.MEMORY
            ),
            memory_swap=host_config.get(
                DockerHostConfigAttrKey.MEMORY_SWAP
            ),
            memory_reservation=host_config.get(
                DockerHostConfigAttrKey.MEMORY_RESERVATION
            ),
            kernel_memory=host_config.get(
                DockerHostConfigAttrKey.KERNEL_MEMORY
            ),
            blkio_weight=host_config.get(
                DockerHostConfigAttrKey.BLKIO_WEIGHT
            ),
            pids_limit=host_config.get(
                DockerHostConfigAttrKey.PIDS_LIMIT
            ),
        )

    def _parse_health_check(
        self,
        health_check: dict[str, Any] | None,
    ) -> HealthCheck | None:
        """Parse health check configuration.
        """
        if not health_check:
            return None

        return HealthCheck(
            test=health_check.get(DockerHealthCheckAttrKey.TEST),
            interval=health_check.get(
                DockerHealthCheckAttrKey.INTERVAL
            ),
            timeout=health_check.get(
                DockerHealthCheckAttrKey.TIMEOUT
            ),
            retries=health_check.get(
                DockerHealthCheckAttrKey.RETRIES
            ),
            start_period=health_check.get(
                DockerHealthCheckAttrKey.START_PERIOD
            ),
        )
