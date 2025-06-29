from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP

from mcp_docker_bridge.shared.context import AppContext
from mcp_docker_bridge.shared.docker_client import DockerClientManager


@asynccontextmanager
async def lifespan(mcp: FastMCP) -> AsyncIterator[AppContext]:
    docker_client = DockerClientManager()
    docker_client.connect()

    try:
        yield AppContext(docker_client=docker_client)
    finally:
        docker_client.disconnect()


def create_mcp() -> FastMCP:
    return FastMCP(
        name='docker-bridge',
        lifespan=lifespan,
    )


mcp = create_mcp()
