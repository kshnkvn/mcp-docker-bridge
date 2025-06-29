from enum import StrEnum


class ContainerState(StrEnum):
    """Container state values for filtering.
    """
    RESTARTING = 'restarting'
    RUNNING = 'running'
    PAUSED = 'paused'
    EXITED = 'exited'


class PortType(StrEnum):
    """Port protocol types.
    """
    TCP = 'tcp'
    UDP = 'udp'


class MountType(StrEnum):
    """Mount types for containers.
    """
    BIND = 'bind'
    VOLUME = 'volume'
    TMPFS = 'tmpfs'
    NPIPE = 'npipe'


class MountMode(StrEnum):
    """Mount modes for Docker containers.

    Includes both traditional read/write modes and SELinux labeling options.
    """
    RW = 'rw'  # Read-write
    RO = 'ro'  # Read-only
    Z_SHARED = 'z'  # SELinux: shared content label (multi-container)
    Z_PRIVATE = 'Z'  # SELinux: private unshared label (single-container)


class MountPropagation(StrEnum):
    """Mount propagation modes.
    """
    SHARED = 'shared'
    SLAVE = 'slave'
    PRIVATE = 'private'
    RSHARED = 'rshared'
    RSLAVE = 'rslave'
    RPRIVATE = 'rprivate'


class ContainerAttrKey(StrEnum):
    """Container attribute keys from Docker API.
    """
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


class StateAttrKey(StrEnum):
    """State dictionary attribute keys from Docker API.
    """
    STATUS = 'Status'
    STARTED_AT = 'StartedAt'
    FINISHED_AT = 'FinishedAt'
    EXIT_CODE = 'ExitCode'


class PortAttrKey(StrEnum):
    """Port attribute keys from Docker API.
    """
    IP = 'IP'
    PRIVATE_PORT = 'PrivatePort'
    PUBLIC_PORT = 'PublicPort'
    TYPE = 'Type'


class MountAttrKey(StrEnum):
    """Mount attribute keys from Docker API.
    """
    TYPE = 'Type'
    NAME = 'Name'
    SOURCE = 'Source'
    DESTINATION = 'Destination'
    DRIVER = 'Driver'
    MODE = 'Mode'
    RW = 'RW'
    PROPAGATION = 'Propagation'


class NetworkAttrKey(StrEnum):
    """Network attribute keys from Docker API.
    """
    NETWORK_MODE = 'NetworkMode'
    NETWORKS = 'Networks'


class FilterKey(StrEnum):
    """Filter keys for Docker API.
    """
    EXITED = 'exited'
    STATUS = 'status'
    LABEL = 'label'
    ID = 'id'
    NAME = 'name'
    ANCESTOR = 'ancestor'
    BEFORE = 'before'
    SINCE = 'since'


class DockerAPIParam(StrEnum):
    """Docker API parameter names for containers.list().
    """
    ALL = 'all'
    SINCE = 'since'
    BEFORE = 'before'
    LIMIT = 'limit'
    FILTERS = 'filters'
    SPARSE = 'sparse'
    IGNORE_REMOVED = 'ignore_removed'



