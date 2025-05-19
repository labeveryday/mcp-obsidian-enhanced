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
from mcp_obsidian.prompts import PROMPTS, get_prompt, list_prompts
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

@mcp.prompt("organize-notes")
async def organize_notes_prompt(
    topic: str,
    folder: str = ""
) -> Dict[str, Any]:
    """Organize notes related to a specific topic."""
    result = await obsidian_organize_notes(topic=topic, folder=folder)
    return {"result": result}

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


@mcp.tool()
async def obsidian_search(query: str) -> List[Dict[str, Any]]:
    """Search for notes in your Obsidian vault.
    
    Searches the entire vault for notes matching the query. By default, searches across all folders
    and files in your vault. You can use search operators to narrow down results:
    
    - path:folder/ - Search only in a specific folder
    - tag:#tag - Search for notes with specific tags
    - file:name.md - Search for specific filenames
    - content:"text" - Search for specific content
    
    The search is case-insensitive by default and returns results with context around matches.
    
    Args:
        query: Search query string
            Examples:
            - "file:hello-world.md" - Find files named hello-world.md
            - "path:AWS-Training file:hello-world.md" - Find hello-world.md in AWS-Training folder
            - "tag:#project" - Find notes with #project tag
            - "content:important" - Find notes containing "important"
    
    Returns:
        List of matching notes with metadata and context around matches
    
    Examples:
        - obsidian_search(query="file:hello-world.md") - Find files named hello-world.md
        - obsidian_search(query="path:AWS-Training") - Find all notes in AWS-Training folder
        - obsidian_search(query="tag:#important") - Find notes with the #important tag
        - obsidian_search(query="content:project") - Find notes containing "project"
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        # If query is just a filename without operators, add the file: operator
        if query.endswith('.md') and ' ' not in query and ':' not in query:
            query = f"file:{query}"
            
        # Use simple search for basic text queries
        # The client will handle the proper Content-Type and request format
        return await client.simple_search(query)
    except ObsidianError as e:
        raise RuntimeError(f"Failed to search: {str(e)}")


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


# Tool for summarizing a note
@mcp.tool()
async def obsidian_summarize_note(path: str, length: str = "medium") -> str:
    """Summarize the content of a note.
    
    Reads a note and generates a summary of its content.
    
    Args:
        path: Path to the note to summarize
        length: Desired length of summary (short, medium, long)
    
    Returns:
        Summary of the note content
    
    Examples:
        - obsidian_summarize_note(path="Meeting Notes.md")
        - obsidian_summarize_note(path="Projects/Research.md", length="short")
        - obsidian_summarize_note(path="Books/Book Review.md", length="long")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        # Read the note content
        content = await client.get_note_content(path)
        
        # Generate summary based on length
        if length == "short":
            summary = f"Short summary of '{path}':\n\n"
            # In a real implementation, this would use an LLM to generate a summary
            # For now, we'll just return a placeholder
            summary += "This is a brief summary of the note content."
        elif length == "long":
            summary = f"Detailed summary of '{path}':\n\n"
            # In a real implementation, this would use an LLM to generate a summary
            # For now, we'll just return a placeholder
            summary += "This is a comprehensive summary of the note content, including all key points and details."
        else:  # medium (default)
            summary = f"Summary of '{path}':\n\n"
            # In a real implementation, this would use an LLM to generate a summary
            # For now, we'll just return a placeholder
            summary += "This is a summary of the main points from the note content."
        
        return summary
    except ObsidianNotFoundError:
        raise ValueError(f"Note not found: {path}")
    except ObsidianError as e:
        raise RuntimeError(f"Failed to summarize note: {str(e)}")


# Tool for searching and compiling notes
@mcp.tool()
async def obsidian_search_and_compile(
    query: str, 
    output_path: Optional[str] = None
) -> str:
    """Search for notes and compile information.
    
    Searches for notes matching the query and compiles the information into a single note.
    
    Args:
        query: Search query
        output_path: Path where to save the compiled note (optional)
    
    Returns:
        Compilation result or path to the saved note
    
    Examples:
        - obsidian_search_and_compile(query="project")
        - obsidian_search_and_compile(query="meeting notes", output_path="Compiled/Meetings.md")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        # Search for notes
        results = await client.search(query)
        
        if not results:
            return f"No results found for query: {query}"
        
        # Compile information
        compilation = f"# Compilation: {query}\n\n"
        compilation += f"Search query: {query}\n"
        compilation += f"Results found: {len(results)}\n\n"
        
        # Add each result
        for i, result in enumerate(results):
            path = result.get("path", "Unknown")
            compilation += f"## {i+1}. {path}\n\n"
            
            try:
                # Get content of the note
                content = await client.get_note_content(path)
                # Add a snippet of the content
                snippet = content[:500] + "..." if len(content) > 500 else content
                compilation += f"{snippet}\n\n"
            except Exception:
                compilation += "Could not retrieve content.\n\n"
            
            compilation += "---\n\n"
        
        # Save to output path if specified
        if output_path:
            await client.create_note(output_path, compilation)
            return f"Compilation saved to {output_path}"
        
        return compilation
    except ObsidianError as e:
        raise RuntimeError(f"Failed to search and compile: {str(e)}")


# Tool for organizing notes
@mcp.tool()
async def obsidian_organize_notes(topic: str, folder: str = "") -> str:
    """Organize notes on a specific topic.
    
    Finds notes related to a topic and suggests an organization structure.
    
    Args:
        topic: Topic to organize notes around
        folder: Folder to organize within (optional)
    
    Returns:
        Organization suggestions
    
    Examples:
        - obsidian_organize_notes(topic="project management")
        - obsidian_organize_notes(topic="research", folder="Academic")
    """
    global client
    
    # Initialize client if needed
    if not client:
        await initialize_client()
    
    try:
        # Search for notes related to the topic
        results = await client.search(topic)
        
        if not results:
            return f"No notes found related to topic: {topic}"
        
        # Generate organization suggestions
        organization = f"# Organization Suggestions for: {topic}\n\n"
        
        if folder:
            organization += f"Within folder: {folder}\n\n"
        
        organization += f"Found {len(results)} related notes.\n\n"
        
        # Group by potential categories (in a real implementation, this would use an LLM)
        organization += "## Suggested Structure\n\n"
        organization += f"1. Create a main index note for '{topic}'\n"
        organization += "2. Group notes into the following categories:\n"
        organization += "   - Overview and Introduction\n"
        organization += "   - Key Concepts\n"
        organization += "   - Examples and Case Studies\n"
        organization += "   - References and Resources\n\n"
        
        # List related notes
        organization += "## Related Notes\n\n"
        for result in results:
            path = result.get("path", "Unknown")
            organization += f"- {path}\n"
        
        return organization
    except ObsidianError as e:
        raise RuntimeError(f"Failed to organize notes: {str(e)}")


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
