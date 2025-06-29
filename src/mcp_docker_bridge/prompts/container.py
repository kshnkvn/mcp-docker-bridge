from mcp.server.fastmcp.prompts import base

from mcp_docker_bridge import mcp


@mcp.prompt(title='List Docker Containers')
def list_containers_guide() -> list[base.Message]:
    """Guide for using the list_containers tool effectively.
    """
    return [
        base.UserMessage(
            'I need help understanding how to use the list_containers tool '
            'in Docker Bridge MCP.'
        ),
        base.AssistantMessage(
            """I'll help you understand the list_containers tool!

The `list_containers` tool provides a clean overview of Docker containers on
your system with essential information only.

**What you'll get for each container:**
- Container ID and names
- Image name
- Current state (running, exited, etc.)
- Complete lifecycle timing:
  - Creation time (when container was created)
  - Start time (when container was last started, if ever)
  - Finish time (when container was last stopped, if applicable)
- Port mappings (if any)

**Primary use cases:**
- Get a list of all running containers
- Get a list of all stopped containers
- Search for a specific container to get its ID
- Check if a container exists and its current state
- Get a quick overview of container states and complete lifecycle timing

**Key parameters:**
- `all` (bool): Show all containers (default: only running)
- `limit` (int): Limit number of results
- `filters`: Filter containers by:
  - `status`: running, exited, paused, etc.
  - `name`: Filter by container name
  - `ancestor`: Filter by source image
  - `label`: Filter by labels

**Examples:**
1. List running containers: `list_containers()`
2. List all containers: `list_containers(params={"all": true})`
3. Find exited containers:
   `list_containers(params={"filters": {"status": "exited"}})`
4. Find containers by name pattern:
   `list_containers(params={"filters": {"name": "web"}})`

This tool provides a simplified view perfect for getting an overview. For
detailed container inspection, use dedicated Docker inspection tools.

What specific container information are you looking for?
"""
        ),
    ]


@mcp.prompt(title='Filter Containers by Status')
def filter_by_status(status: str = 'exited') -> str:
    """Generate a prompt for filtering containers by status.
    """
    return f"""Please list all Docker containers with status '{status}'.

Use the list_containers tool with status filtering to show containers
currently in the '{status}' state. This will help identify:
- Container names and IDs
- Current state
- Complete lifecycle timing (created, started, finished)
- Basic container information for further investigation
"""


@mcp.prompt(title='Find Container by Name')
def find_by_name(name_pattern: str = 'web') -> str:
    """Generate a prompt to find containers by name pattern.
    """
    return f"""Please find Docker containers with names containing
'{name_pattern}'.

Use the list_containers tool with name filtering to locate containers
matching this pattern. This is useful for:
- Getting container IDs for further operations
- Checking if specific containers exist
- Verifying container naming conventions
"""


@mcp.prompt(title='Container Overview')
def container_overview() -> list[base.Message]:
    """Generate a basic overview of container states.
    """
    return [
        base.UserMessage(
            'Can you give me an overview of my Docker containers?'
        ),
        base.AssistantMessage(
            """I'll provide an overview of your Docker containers using the
list_containers tool.

I can show you:
- How many containers are currently running vs stopped
- Container names and their current states
- What images they're based on
- Complete lifecycle timing (created, started, finished)
- Basic port mappings

This gives you a quick snapshot of your Docker environment with essential
information. For detailed container inspection (logs, detailed config, etc.),
you'll need to use other Docker tools.
"""
        ),
    ]


@mcp.prompt(title='Check Container Existence')
def check_container_exists(container_name: str = 'my-app') -> str:
    """Generate a prompt to check if a specific container exists.
    """
    return f"""Please check if a container named '{container_name}' exists
and show its current state.

Use the list_containers tool with name filtering to:
- Verify the container exists on the system
- Check its current state (running, stopped, etc.)
- Get its container ID for potential further operations
- See complete lifecycle timing (created, started, finished)

If the container doesn't exist, the list will be empty.
"""


@mcp.prompt(title='Find Containers by Image')
def find_by_image(image_name: str = 'nginx') -> str:
    """Generate a prompt to find containers from a specific image.
    """
    return f"""Please find all Docker containers created from the
'{image_name}' image.

Use the list_containers tool with the ancestor filter to locate containers
based on their source image. This helps with:
- Inventory management of containers by image type
- Finding all instances of a particular application
- Getting container IDs and states for image-specific operations
"""


@mcp.prompt(title='Recent Container Activity')
def recent_activity() -> str:
    """Generate a prompt to check recent container activity.
    """
    return """Please show recent Docker container activity.

Use the list_containers tool to get an overview of:
- Currently running containers with their states
- Recently stopped containers (use all=true)
- Complete lifecycle timing to identify recent activity
  (created, started, finished)

This provides insight into recent Docker activity on the system with
essential container information.
"""
