from typing import Any

from docker.errors import APIError
from mcp.server.fastmcp import Context

from mcp_docker_bridge import mcp
from mcp_docker_bridge.shared.context import AppContext
from mcp_docker_bridge.shared.schemas import (
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

        return ListContainersResponse(
            containers=containers,
            total_count=len(containers),
        )

    except APIError as e:
        raise RuntimeError(f'Docker API error: {e}')
    except Exception as e:
        raise RuntimeError(f'Unexpected error listing containers: {e}')
