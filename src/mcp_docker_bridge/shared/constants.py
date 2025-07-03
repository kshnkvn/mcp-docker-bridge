from enum import StrEnum


class DockerContainerState(StrEnum):
    """Docker container state values for filtering.
    """
    RESTARTING = 'restarting'
    RUNNING = 'running'
    PAUSED = 'paused'
    EXITED = 'exited'
    CREATED = 'created'
    REMOVING = 'removing'
    DEAD = 'dead'


class DockerPortType(StrEnum):
    """Docker container port protocol types.
    """
    TCP = 'tcp'
    UDP = 'udp'


class DockerContainerAttrKey(StrEnum):
    """Docker container attribute keys from Docker API.
    """
    ID = 'Id'
    NAMES = 'Names'
    IMAGE = 'Image'
    IMAGE_ID = 'ImageID'
    COMMAND = 'Command'
    CREATED = 'Created'
    PORTS = 'Ports'
    LABELS = 'Labels'
    STATE = 'State'
    HOST_CONFIG = 'HostConfig'
    NETWORK_SETTINGS = 'NetworkSettings'
    MOUNTS = 'Mounts'
    SIZE_RW = 'SizeRw'
    SIZE_ROOT_FS = 'SizeRootFs'
    NETWORKS = 'Networks'


class DockerContainerStateAttrKey(StrEnum):
    """Docker container state dictionary attribute keys from Docker API.
    """
    STATUS = 'Status'
    STARTED_AT = 'StartedAt'
    FINISHED_AT = 'FinishedAt'
    EXIT_CODE = 'ExitCode'
    ERROR = 'Error'
    RUNNING = 'Running'
    PAUSED = 'Paused'
    RESTARTING = 'Restarting'
    PID = 'Pid'


class DockerContainerPortAttrKey(StrEnum):
    """Docker container port attribute keys from Docker API.
    """
    IP = 'IP'
    PRIVATE_PORT = 'PrivatePort'
    PUBLIC_PORT = 'PublicPort'
    TYPE = 'Type'


class DockerContainerFilterKey(StrEnum):
    """Docker container filter keys for Docker API.
    """
    EXITED = 'exited'
    STATUS = 'status'
    LABEL = 'label'
    ID = 'id'
    NAME = 'name'
    ANCESTOR = 'ancestor'
    BEFORE = 'before'
    SINCE = 'since'


class DockerConfigAttrKey(StrEnum):
    """Docker container Config section attribute keys.
    """
    IMAGE = 'Image'
    CMD = 'Cmd'
    ENTRYPOINT = 'Entrypoint'
    ENV = 'Env'
    WORKING_DIR = 'WorkingDir'
    USER = 'User'
    HOSTNAME = 'Hostname'
    DOMAINNAME = 'Domainname'
    LABELS = 'Labels'
    EXPOSED_PORTS = 'ExposedPorts'
    VOLUMES = 'Volumes'
    TTY = 'Tty'
    OPEN_STDIN = 'OpenStdin'
    HEALTHCHECK = 'Healthcheck'


class DockerHostConfigAttrKey(StrEnum):
    """Docker container HostConfig section attribute keys.
    """
    BINDS = 'Binds'
    PORT_BINDINGS = 'PortBindings'
    RESTART_POLICY = 'RestartPolicy'
    NETWORK_MODE = 'NetworkMode'
    PRIVILEGED = 'Privileged'
    CAP_ADD = 'CapAdd'
    CAP_DROP = 'CapDrop'
    EXTRA_HOSTS = 'ExtraHosts'
    GROUP_ADD = 'GroupAdd'
    SECURITY_OPT = 'SecurityOpt'
    LOG_CONFIG = 'LogConfig'
    CPU_SHARES = 'CpuShares'
    CPU_PERIOD = 'CpuPeriod'
    CPU_QUOTA = 'CpuQuota'
    CPUSET_CPUS = 'CpusetCpus'
    CPUSET_MEMS = 'CpusetMems'
    MEMORY = 'Memory'
    MEMORY_SWAP = 'MemorySwap'
    MEMORY_RESERVATION = 'MemoryReservation'
    KERNEL_MEMORY = 'KernelMemory'
    BLKIO_WEIGHT = 'BlkioWeight'
    PIDS_LIMIT = 'PidsLimit'


class DockerNetworkAttrKey(StrEnum):
    """Docker network endpoint attribute keys.
    """
    NETWORK_ID = 'NetworkID'
    ENDPOINT_ID = 'EndpointID'
    GATEWAY = 'Gateway'
    IP_ADDRESS = 'IPAddress'
    IP_PREFIX_LEN = 'IPPrefixLen'
    IPV6_GATEWAY = 'IPv6Gateway'
    GLOBAL_IPV6_ADDRESS = 'GlobalIPv6Address'
    GLOBAL_IPV6_PREFIX_LEN = 'GlobalIPv6PrefixLen'
    MAC_ADDRESS = 'MacAddress'


class DockerMountAttrKey(StrEnum):
    """Docker mount attribute keys.
    """
    TYPE = 'Type'
    SOURCE = 'Source'
    DESTINATION = 'Destination'
    MODE = 'Mode'
    RW = 'RW'
    PROPAGATION = 'Propagation'


class DockerTopLevelAttrKey(StrEnum):
    """Docker container top-level attribute keys.
    """
    ID_FULL = 'Id'
    CONFIG = 'Config'
    HOST_CONFIG = 'HostConfig'
    STATE = 'State'
    NETWORK_SETTINGS = 'NetworkSettings'
    MOUNTS = 'Mounts'
    PATH = 'Path'
    CREATED = 'Created'
    NAME = 'Name'
    IMAGE = 'Image'


class DockerRestartPolicyAttrKey(StrEnum):
    """Docker restart policy attribute keys.
    """
    NAME = 'Name'
    MAXIMUM_RETRY_COUNT = 'MaximumRetryCount'


class DockerHealthCheckAttrKey(StrEnum):
    """Docker health check attribute keys.
    """
    TEST = 'Test'
    INTERVAL = 'Interval'
    TIMEOUT = 'Timeout'
    RETRIES = 'Retries'
    START_PERIOD = 'StartPeriod'
