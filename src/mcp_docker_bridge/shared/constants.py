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


class DockerContainerStateAttrKey(StrEnum):
    """Docker container state dictionary attribute keys from Docker API.
    """
    STATUS = 'Status'
    STARTED_AT = 'StartedAt'
    FINISHED_AT = 'FinishedAt'
    EXIT_CODE = 'ExitCode'


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
