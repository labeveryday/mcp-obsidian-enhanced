"""
Base tool handler class for the Obsidian MCP server.

This module defines the base ToolHandler class that all tool handlers will inherit from.
It provides common functionality for tool registration, validation, and execution.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Union

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from mcp_obsidian.obsidian import ObsidianClient
from mcp_obsidian.utils.errors import ValidationError, format_error_for_mcp


class ToolHandler(ABC):
    """Base class for all tool handlers."""

    def __init__(self, tool_name: str):
        """
        Initialize the tool handler.
        
        Args:
            tool_name: Name of the tool.
        """
        self.name = tool_name
        self.obsidian_client = ObsidianClient()

    @abstractmethod
    def get_tool_description(self) -> Tool:
        """
        Get the tool description for MCP.
        
        Returns:
            Tool description.
        """
        pass

    @abstractmethod
    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """
        Execute the tool with the given arguments.
        
        Args:
            args: Tool arguments.
            
        Returns:
            Sequence of content items.
        """
        pass

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the tool arguments.
        
        Args:
            args: Tool arguments.
            
        Returns:
            Validated arguments.
            
        Raises:
            ValidationError: If validation fails.
        """
        # Default implementation does no validation
        return args

    def format_response(self, data: Any) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """
        Format the response for MCP.
        
        Args:
            data: Data to format.
            
        Returns:
            Formatted response.
        """
        if isinstance(data, str):
            return [TextContent(type="text", text=data)]
        elif isinstance(data, (list, dict)):
            import json
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        else:
            return [TextContent(type="text", text=str(data))]

    def handle_error(self, error: Exception) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """
        Handle an error and format it for MCP.
        
        Args:
            error: Exception to handle.
            
        Returns:
            Formatted error response.
        """
        error_data = format_error_for_mcp(error)
        return [TextContent(
            type="text", 
            text=f"Error: {error_data['error']['message']}"
        )]


class FileOperationToolHandler(ToolHandler):
    """Base class for file operation tool handlers."""

    def validate_filepath(self, filepath: Optional[str]) -> str:
        """
        Validate a file path.
        
        Args:
            filepath: File path to validate.
            
        Returns:
            Validated file path.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not filepath:
            raise ValidationError("File path is required")
        
        # Remove leading slash if present
        if filepath.startswith("/"):
            filepath = filepath[1:]
            
        return filepath


class ActiveFileToolHandler(ToolHandler):
    """Base class for active file tool handlers."""
    
    def __init__(self, tool_name: str):
        """Initialize the active file tool handler."""
        super().__init__(tool_name)


class FolderOperationToolHandler(ToolHandler):
    """Base class for folder operation tool handlers."""
    
    def validate_dirpath(self, dirpath: Optional[str]) -> str:
        """
        Validate a directory path.
        
        Args:
            dirpath: Directory path to validate.
            
        Returns:
            Validated directory path.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not dirpath:
            raise ValidationError("Directory path is required")
        
        # Remove leading slash if present
        if dirpath.startswith("/"):
            dirpath = dirpath[1:]
            
        # Ensure path ends with a slash
        if not dirpath.endswith("/"):
            dirpath = f"{dirpath}/"
            
        return dirpath


class SearchToolHandler(ToolHandler):
    """Base class for search tool handlers."""
    
    def validate_query(self, query: Optional[str]) -> str:
        """
        Validate a search query.
        
        Args:
            query: Query to validate.
            
        Returns:
            Validated query.
            
        Raises:
            ValidationError: If validation fails.
        """
        if not query:
            raise ValidationError("Search query is required")
        return query
