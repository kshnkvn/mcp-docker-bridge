from dataclasses import dataclass

from mcp_docker_bridge.shared.docker_client import DockerClientManager


@dataclass
class AppContext:
    docker_client: DockerClientManager
