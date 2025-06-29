import sys

from loguru import logger

from mcp_docker_bridge import mcp
from mcp_docker_bridge.prompts import (  # noqa: F401
    check_container_exists,
    container_overview,
    filter_by_status,
    find_by_image,
    find_by_name,
    list_containers_guide,
    recent_activity,
)
from mcp_docker_bridge.tools import list_containers  # noqa: F401


def main():
    """Main entry point for the MCP server.
    """
    logger.info('Starting MCP Docker Bridge Server...')
    logger.info(f'Server name: {mcp.name}')
    logger.info(f'Host: {mcp.settings.host}')
    logger.info(f'Port: {mcp.settings.port}')
    logger.info(f'Debug mode: {mcp.settings.debug}')
    logger.info(f'Log level: {mcp.settings.log_level}')
    logger.info('Tools registered successfully')
    logger.info('Server ready - waiting for MCP client connections...')

    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info('Server stopped')
    except Exception as e:
        logger.error(f'Server error: {e}')
        sys.exit(1)
    finally:
        logger.info('Server shutdown complete')


if __name__ == '__main__':
    main()
