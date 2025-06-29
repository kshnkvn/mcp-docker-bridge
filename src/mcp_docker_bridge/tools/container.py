from typing import Any

from mcp.server.fastmcp import Context

from mcp_docker_bridge import mcp
from mcp_docker_bridge.shared.context import AppContext


@mcp.tool()
def list_containers(ctx: Context[Any, AppContext]) -> None:
    """List containers
    """
    app_context: AppContext = ctx.request_context.lifespan_context
    print(app_context)
