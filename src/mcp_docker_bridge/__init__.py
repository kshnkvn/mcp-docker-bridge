from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from mcp_docker_bridge.shared.context import AppContext


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[AppContext]:
    yield AppContext()


def create_mcp() -> FastMCP:
    return FastMCP(
        name='docker-bridge',
        lifespan=lifespan,
    )


mcp = create_mcp()
