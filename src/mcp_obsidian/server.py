"""
MCP server implementation for the Obsidian MCP server.

This module implements the MCP server that handles requests from MCP clients
and routes them to the appropriate tool handlers.
"""

import logging
import sys
from typing import Any, Dict, List, Optional, Type

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from mcp_obsidian.config import get_config
from mcp_obsidian.tools.base import ToolHandler
from mcp_obsidian.utils.errors import ObsidianError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("mcp_obsidian")


class ObsidianMCPServer:
    """MCP server for Obsidian integration."""

    def __init__(self):
        """Initialize the MCP server."""
        config = get_config()
        
        # Set log level from configuration
        logger.setLevel(config.log_level)
        
        # Initialize MCP server
        self.server = Server(
            name="mcp-obsidian",
            version="0.1.0",
            capabilities={
                "tools": {},
            }
        )
        
        # Initialize tool registry
        self.tools: Dict[str, ToolHandler] = {}
        
        # Set up error handling
        self.server.onerror = self._handle_error
        
    def register_tool(self, tool_handler: ToolHandler) -> None:
        """
        Register a tool handler with the server.
        
        Args:
            tool_handler: Tool handler to register.
        """
        tool_name = tool_handler.name
        self.tools[tool_name] = tool_handler
        logger.info(f"Registered tool: {tool_name}")
        
    def register_tools(self, tool_handlers: List[Type[ToolHandler]]) -> None:
        """
        Register multiple tool handlers with the server.
        
        Args:
            tool_handlers: List of tool handler classes to register.
        """
        for handler_class in tool_handlers:
            handler = handler_class()
            self.register_tool(handler)
    
    def _handle_list_tools(self) -> List[Tool]:
        """
        Handle list_tools request.
        
        Returns:
            List of tool descriptions.
        """
        return [handler.get_tool_description() for handler in self.tools.values()]
    
    def _handle_call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call_tool request.
        
        Args:
            name: Name of the tool to call.
            arguments: Tool arguments.
            
        Returns:
            Tool response.
            
        Raises:
            ObsidianError: If the tool is not found or execution fails.
        """
        logger.debug(f"Calling tool: {name} with arguments: {arguments}")
        
        # Find the tool handler
        handler = self.tools.get(name)
        if not handler:
            raise ObsidianError(f"Tool not found: {name}")
        
        try:
            # Validate arguments
            validated_args = handler.validate_args(arguments)
            
            # Run the tool
            result = handler.run_tool(validated_args)
            
            # Return the result
            return {"content": result}
        except Exception as e:
            logger.error(f"Error executing tool {name}: {str(e)}", exc_info=True)
            if isinstance(e, ObsidianError):
                raise
            raise ObsidianError(f"Error executing tool {name}: {str(e)}") from e
    
    def _handle_error(self, error: Exception) -> None:
        """
        Handle server error.
        
        Args:
            error: Exception that occurred.
        """
        logger.error(f"Server error: {str(error)}", exc_info=True)
    
    def setup_handlers(self) -> None:
        """Set up request handlers."""
        # Register handlers
        self.server.set_list_tools_handler(self._handle_list_tools)
        self.server.set_call_tool_handler(self._handle_call_tool)
    
    def run(self) -> None:
        """Run the server."""
        logger.info("Starting MCP server...")
        
        # Set up handlers
        self.setup_handlers()
        
        try:
            # Run the server using stdio
            stdio_server(self.server)
            logger.info("Server started successfully")
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}", exc_info=True)
            sys.exit(1)


def main() -> None:
    """Entry point for the MCP server."""
    try:
        # Create and run server
        server = ObsidianMCPServer()
        
        # TODO: Register tool handlers here
        # Example: server.register_tools([ReadNoteToolHandler, CreateNoteToolHandler])
        
        # Run the server
        server.run()
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
