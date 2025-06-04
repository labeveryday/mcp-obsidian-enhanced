"""MCP server implementation using FastMCP for Obsidian integration."""

import logging
import sys
import os
import platform
from typing import Dict, Any, List, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
import mcp

from mcp_obsidian.config import load_config
from mcp_obsidian.obsidian import ObsidianClient
from mcp_obsidian.utils.errors import (
    ObsidianError,
    ObsidianNotFoundError,
    ConfigurationError
)

# Version of this MCP server
__version__ = "0.1.0"

# Try to get MCP version
try:
    mcp_version = getattr(mcp, "__version__", "unknown")
except:
    mcp_version = "unknown"

# Configure logging to stderr only with color support
class ColoredFormatter(logging.Formatter):
    """Custom formatter with colored output."""
    
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',   # Green
        'WARNING': '\033[93m', # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[91m\033[1m',  # Bold Red
        'RESET': '\033[0m'    # Reset
    }
    
    def format(self, record):
        log_message = super().format(record)
        level_name = record.levelname
        if level_name in self.COLORS:
            return f"{self.COLORS[level_name]}{log_message}{self.COLORS['RESET']}"
        return log_message

# Set up logger
logger = logging.getLogger("mcp_obsidian")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Initialize FastMCP server with proper configuration
mcp = FastMCP(
    name="Obsidian MCP Server",
    version=__version__,
    capabilities={
        "tools": True,
        "resources": True,
        "prompts": True
    }
)

# Register prompts using decorators
@mcp.prompt("meeting-notes")
async def meeting_notes_prompt(
    title: str,
    date: str = "",
    participants: str = "",
    folder: str = "Meetings",
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create a meeting note with the given details."""
    global client
    if not client:
        await initialize_client()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    if not folder.endswith("/"):
        folder += "/"
    folder_note_path = f"{folder}.folder"
    folder_note_content = f"# {folder.rstrip('/')}\nThis folder contains meeting notes."
    try:
        await client.create_note(folder_note_path, folder_note_content)
    except Exception as e:
        if "already exists" not in str(e):
            raise e
    content = f"""# {title}\n\nDate: {date}\nParticipants: {participants}\n\n## Agenda\n- \n\n## Notes\n- \n\n## Action Items\n- [ ] \n\n## Next Steps\n- \n\n---\ntags: [meeting]\n"""
    path = f"{folder}{title}.md"
    success = await client.create_note(path, content)
    return {
        "status": "success" if success else "error",
        "path": path,
        "content": content
    }

@mcp.prompt("create-note")
async def create_note_prompt(
    title: str,
    content: str,
    folder: str = "",
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create a new note with the given details."""
    path = f"{folder}/{title}.md" if folder else f"{title}.md"
    success = await obsidian_create_note(
        path=path,
        content=content,
        metadata={"tags": tags} if tags else None
    )
    return {"success": success, "path": path}

# Organize notes prompt removed - planned for Phase 2

# Global client instance
client: Optional[ObsidianClient] = None


# Initialize client
async def initialize_client():
    """Initialize the Obsidian client."""
    global client
    
    if client is not None:
        logger.debug("Client already initialized, reusing existing client")
        return
    
    logger.info("Initializing Obsidian client...")
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not config.api_key:
        logger.error("Missing API key in configuration")
        raise ConfigurationError("Missing required configuration. Please set OBSIDIAN_API_KEY.")
    
    # Initialize Obsidian client
    client = ObsidianClient(config)
    logger.info(f"Connecting to Obsidian API at {config.protocol}://{config.host}:{config.port}")
    
    # Test connection
    try:
        connected = await client.connect()
        if not connected:
            logger.error("Failed to connect to Obsidian API")
            raise ConfigurationError("Failed to connect to Obsidian API")
        logger.info("✅ Successfully connected to Obsidian API")
    except ObsidianError as e:
        logger.error(f"Failed to connect to Obsidian API: {str(e)}")
        raise ConfigurationError(f"Failed to connect to Obsidian API: {str(e)}")


# File operation tools
@mcp.tool()
async def obsidian_read_note(path: str, include_metadata: bool = False) -> str:
    """Get content of a note from your Obsidian vault.
    
    Retrieves the content of a specific note from the currently open Obsidian vault.
    
    Args:
        path: Path to the note relative to vault root (e.g., "Folder/Note.md" or "Note.md")
            - Must include the .md extension
            - Case-sensitive
            - Use forward slashes (/) for folder separators
        include_metadata: Whether to include YAML frontmatter metadata (default: False)
    
    Returns:
        The content of the note as text
    
    Examples:
        - obsidian_read_note(path="Meeting Notes.md")
        - obsidian_read_note(path="Projects/Website/Ideas.md")
        - obsidian_read_note(path="Daily Notes/2025-05-17.md", include_metadata=True)
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.get_note_content(path, include_metadata)
    except ObsidianNotFoundError:
        raise ValueError(f"Note not found: {path}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to read note: {str(e)}")


@mcp.tool()
async def obsidian_create_note(
    path: str, 
    content: str, 
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Create a new note in your Obsidian vault.
    
    Creates a new markdown note at the specified path in the currently open Obsidian vault.
    If the note already exists, it will be overwritten.
    
    Args:
        path: Path where to create the note relative to vault root (e.g., "Folder/Note.md" or "Note.md")
            - Must include the .md extension
            - Case-sensitive
            - Use forward slashes (/) for folder separators
            - Parent folders will be created automatically if they don't exist
        content: Content of the note (markdown text)
        metadata: Optional YAML frontmatter metadata as a dictionary (default: None)
    
    Returns:
        True if successful
    
    Examples:
        - obsidian_create_note(path="Project Ideas.md", content="# Project Ideas\n\n- First idea\n- Second idea")
        - obsidian_create_note(
            path="Projects/Website/Tasks.md", 
            content="# Website Tasks\n\n1. Design homepage\n2. Create navigation",
            metadata={"tags": ["project", "website"], "status": "in-progress"}
          )
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.create_note(path, content, metadata)
    except ObsidianError as e:
        raise RuntimeError(f"Failed to create note: {str(e)}")


@mcp.tool()
async def obsidian_update_note(path: str, content: str) -> bool:
    """Update an existing note in your Obsidian vault.
    
    Updates the content of an existing note in the currently open Obsidian vault.
    This will replace the entire content of the note.
    
    Args:
        path: Path to the note relative to vault root (e.g., "Folder/Note.md" or "Note.md")
            - Must include the .md extension
            - Case-sensitive
            - Use forward slashes (/) for folder separators
        content: New content for the note (markdown text)
    
    Returns:
        True if successful
    
    Examples:
        - obsidian_update_note(path="Meeting Notes.md", content="# Updated Meeting Notes\n\n- New item 1\n- New item 2")
        - obsidian_update_note(path="Projects/Website/Ideas.md", content="# Revised Website Ideas\n\n## New Section\n\nContent here...")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.update_note(path, content)
    except ObsidianNotFoundError:
        raise ValueError(f"Note not found: {path}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to update note: {str(e)}")


@mcp.tool()
async def obsidian_append_note(path: str, content: str) -> bool:
    """Append content to an existing note in your Obsidian vault.
    
    Adds new content to the end of an existing note in the currently open Obsidian vault.
    The original content is preserved, and the new content is added after it.
    
    Args:
        path: Path to the note relative to vault root (e.g., "Folder/Note.md" or "Note.md")
            - Must include the .md extension
            - Case-sensitive
            - Use forward slashes (/) for folder separators
        content: Content to append (markdown text)
    
    Returns:
        True if successful
    
    Examples:
        - obsidian_append_note(path="Meeting Notes.md", content="\n\n## Follow-up Items\n\n- Contact team members\n- Schedule next meeting")
        - obsidian_append_note(path="Projects/Website/Ideas.md", content="\n\n## Additional Ideas\n\n- New feature suggestion\n- Design improvement")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.append_to_note(path, content)
    except ObsidianNotFoundError:
        raise ValueError(f"Note not found: {path}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to append to note: {str(e)}")


@mcp.tool()
async def obsidian_delete_note(path: str) -> bool:
    """Delete a note from your Obsidian vault.
    
    Permanently deletes a note from the currently open Obsidian vault.
    This action cannot be undone.
    
    Args:
        path: Path to the note relative to vault root (e.g., "Folder/Note.md" or "Note.md")
            - Must include the .md extension
            - Case-sensitive
            - Use forward slashes (/) for folder separators
    
    Returns:
        True if successful
    
    Examples:
        - obsidian_delete_note(path="Temporary Notes.md")
        - obsidian_delete_note(path="Projects/Archive/Old Project.md")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.delete_note(path)
    except ObsidianNotFoundError:
        raise ValueError(f"Note not found: {path}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to delete note: {str(e)}")


@mcp.tool()
async def obsidian_list_files(folder: str = "") -> List[Dict[str, Any]]:
    """List files and folders in your Obsidian vault.
    
    Lists all files and folders at the specified path in the currently open Obsidian vault.
    
    Args:
        folder: Folder path relative to vault root (default: "" for root folder)
            - Use empty string ("") to list files/folders at the vault root
            - For subfolders, include trailing slash (e.g., "Projects/" or "Projects/Website/")
            - Case-sensitive
            - Use forward slashes (/) for folder separators
    
    Returns:
        List of files and folders with metadata (type, path, name, etc.)
    
    Examples:
        - obsidian_list_files() - Lists all files/folders at vault root
        - obsidian_list_files(folder="") - Same as above, lists vault root
        - obsidian_list_files(folder="Projects/") - Lists contents of Projects folder
        - obsidian_list_files(folder="Daily Notes/") - Lists contents of Daily Notes folder
    
    Note:
        The trailing slash (/) is important for folder paths. "Projects/" is recognized as a folder,
        while "Projects" might be treated as a file.
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    # Ensure folder path ends with a slash if not empty
    if folder and not folder.endswith("/"):
        folder = folder + "/"
    
    try:
        return await client.list_files(folder)
    except ObsidianNotFoundError:
        raise ValueError(f"Folder not found: {folder}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to list files: {str(e)}")


# Search functionality removed - planned for Phase 2


@mcp.tool()
async def obsidian_get_active_file() -> Dict[str, Any]:
    """Get the currently active file in Obsidian.
    
    Retrieves information about the file that is currently open and active in the Obsidian interface.
    
    Returns:
        Information about the active file (path, name, etc.)
    
    Example:
        - obsidian_get_active_file() - Returns details about the currently open note
    
    Note:
        This requires Obsidian to be open with a file actively selected.
        Returns an error if no file is currently active.
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        return await client.get_active_file()
    except ObsidianError as e:
        raise RuntimeError(f"Failed to get active file: {str(e)}")


# Tool for creating a daily note
@mcp.tool()
async def obsidian_create_daily_note(folder: str = "Daily Notes", tags: List[str] = None) -> bool:
    """Create a daily note with predefined sections.
    
    Creates a new daily note with the current date as the title and predefined sections
    for tasks, meetings, notes, and reflections.
    
    Args:
        folder: Folder to create the daily note in (default: "Daily Notes")
        tags: List of tags to include in the note (default: ["daily"])
    
    Returns:
        True if successful
    
    Examples:
        - obsidian_create_daily_note()
        - obsidian_create_daily_note(folder="Work/Daily")
        - obsidian_create_daily_note(folder="Personal/Journal", tags=["journal", "reflection"])
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    # Get today's date
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Ensure folder path ends with a slash if not empty
    if folder and not folder.endswith("/"):
        folder = folder + "/"
    
    # Create path for the daily note
    path = f"{folder}{today}.md"
    
    # Set up tags
    if tags is None:
        tags = ["daily"]
    
    # Create metadata
    metadata = {
        "date": today,
        "tags": tags
    }
    
    # Create content
    content = f"""# Daily Note: {today}

## Tasks
- [ ] Task 1
- [ ] Task 2
- [ ] Task 3

## Meetings
- 

## Notes
- 

## Reflections
- 
"""
    
    try:
        return await client.create_note(path, content, metadata)
    except ObsidianError as e:
        raise RuntimeError(f"Failed to create daily note: {str(e)}")


# Note summarization removed - planned for Phase 2


# Search and compile functionality removed - planned for Phase 2


# Note organization functionality removed - planned for Phase 2


def run_server():
    """Run the MCP server."""
    # Print banner
    print("\n" + "=" * 60)
    print(f"  Obsidian MCP Server v{__version__}")
    print(f"  MCP SDK Version: {mcp_version}")
    print(f"  Python: {platform.python_version()} on {platform.system()}")
    print("=" * 60)
    
    # Log startup information
    logger.info(f"Starting Obsidian MCP Server v{__version__}")
    logger.info(f"System: {platform.system()} {platform.release()} ({os.name})")
    logger.info(f"Python: {platform.python_version()}")
    logger.info(f"MCP SDK: {mcp_version}")
    
    # Log available tools
    tool_count = len([attr for attr in dir(sys.modules[__name__]) if attr.startswith('obsidian_')])
    logger.info(f"Registered {tool_count} Obsidian tools")
    
    # Log transport information
    logger.info("Using stdio transport for communication")
    logger.info("Starting server...")
    
    try:
        # Run the server
        print("\nServer is running. Press Ctrl+C to stop.\n")
        mcp.run(transport="stdio")
        logger.info("Server started successfully")
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")
