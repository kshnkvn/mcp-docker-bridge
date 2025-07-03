from dataclasses import dataclass, field

from mcp_docker_bridge.shared.docker_client import DockerClientManager
from mcp_docker_bridge.shared.schemas import (
    ContainerInfo,
    DetailedContainerInfo,
)


@dataclass
class AppContext:
    docker_client: DockerClientManager
    # Cache for detailed container information
    detailed_container_cache: dict[str, DetailedContainerInfo] = field(
        default_factory=dict
    )
    # Cache for basic container information from list_containers
    basic_container_cache: dict[str, ContainerInfo] = field(
        default_factory=dict
    )

    def cache_detailed_container(
        self, container_id: str, container_info: DetailedContainerInfo
    ) -> None:
        """Cache detailed container information by ID.
        """
        self.detailed_container_cache[container_id] = container_info
        # Also cache by names for quick lookup
        for name in container_info.names:
            self.detailed_container_cache[name] = container_info

    def cache_basic_container(self, container_info: ContainerInfo) -> None:
        """Cache basic container information from list operation.
        """
        self.basic_container_cache[container_info.id] = container_info
        # Also cache by names for quick lookup
        for name in container_info.names:
            self.basic_container_cache[name] = container_info

    def get_cached_detailed_container(
        self, container_id: str
    ) -> DetailedContainerInfo | None:
        """Retrieve cached detailed container information if available.
        """
        return self.detailed_container_cache.get(container_id)

    def get_cached_basic_container(
        self, container_id: str
    ) -> ContainerInfo | None:
        """Retrieve cached basic container information if available.
        """
        return self.basic_container_cache.get(container_id)

    def clear_container_cache(self, container_id: str | None = None) -> None:
        """Clear specific container from cache or entire cache.
        """
        if container_id:
            # Clear from detailed cache
            container = self.detailed_container_cache.get(container_id)
            if container:
                self.detailed_container_cache.pop(container_id, None)
                for name in container.names:
                    self.detailed_container_cache.pop(name, None)

            # Clear from basic cache
            basic_container = self.basic_container_cache.get(container_id)
            if basic_container:
                self.basic_container_cache.pop(container_id, None)
                for name in basic_container.names:
                    self.basic_container_cache.pop(name, None)
        else:
            self.detailed_container_cache.clear()
            self.basic_container_cache.clear()
