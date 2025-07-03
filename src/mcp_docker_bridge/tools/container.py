from typing import Any

from docker.errors import APIError
from loguru import logger
from mcp.server.fastmcp import Context

from mcp_docker_bridge import mcp
from mcp_docker_bridge.shared.context import AppContext
from mcp_docker_bridge.shared.schemas import (
    DetailedContainerInfo,
    GetContainerParams,
    ListContainersParams,
    ListContainersResponse,
)


@mcp.tool()
def list_containers(
    ctx: Context[Any, AppContext],
    params: ListContainersParams | None = None,
) -> ListContainersResponse:
    """List Docker containers with optional filtering and parameters.

    This tool provides comprehensive container listing functionality.
    It shows running containers by default, or all containers when requested.

    Args:
        ctx: MCP context with AppContext
        params: Optional parameters for filtering and controlling the output

    Returns:
        ListContainersResponse with list of containers and total count

    Raises:
        RuntimeError: If Docker API returns an error
    """
    app_context: AppContext = ctx.request_context.lifespan_context
    docker_client = app_context.docker_client

    try:
        containers = docker_client.list_containers(params)

        # Cache each container for future get_container calls
        for container in containers:
            app_context.cache_basic_container(container)

        return ListContainersResponse(
            containers=containers,
            total_count=len(containers),
        )

    except APIError as e:
        raise RuntimeError(f'Docker API error: {e}')
    except Exception as e:
        raise RuntimeError(f'Unexpected error listing containers: {e}')


@mcp.tool()
def get_container(
    ctx: Context[Any, AppContext],
    params: GetContainerParams,
) -> DetailedContainerInfo:
    """Get detailed information about a specific Docker container.

    This tool retrieves comprehensive container information including:
    - Configuration (image, command, environment, etc.)
    - Runtime state (running, paused, exit code, etc.)
    - Networking (ports, networks, IP addresses)
    - Storage (mounts, volumes)
    - Resource limits and policies

    The information is sufficient to recreate the container with the same
    configuration. Results are cached for performance.

    Args:
        ctx: MCP context with app context
        params: Container ID/name and cache settings

    Returns:
        Detailed container information

    Raises:
        RuntimeError: If container not found or Docker connection fails
    """
    app_context: AppContext = ctx.request_context.lifespan_context
    container_id = params.container_id

    # Check detailed cache if enabled
    if params.use_cache:
        cached_info = app_context.get_cached_detailed_container(container_id)
        if cached_info:
            logger.debug(
                f'Returning cached detailed info for container {container_id}'
            )
            return cached_info

    # Check if we have basic info from list_containers
    basic_info = app_context.get_cached_basic_container(container_id)
    if basic_info:
        logger.debug(
            f'Found basic info for container {container_id} from previous '
            'list operation'
        )

    # Fetch from Docker
    try:
        container_info = app_context.docker_client.get_container(container_id)

        # Cache the detailed result
        app_context.cache_detailed_container(container_info.id, container_info)

        return container_info

    except Exception as e:
        logger.error(f'Failed to get container {container_id}: {e}')
        raise RuntimeError(f'Failed to get container information: {str(e)}')
