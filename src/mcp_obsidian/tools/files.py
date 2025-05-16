"""
File operation tools for the Obsidian MCP server.

This module implements tool handlers for basic file operations:
- Reading file content
- Creating or updating files
- Appending content to files
- Patching content at specific locations
- Deleting files
"""

import json
from typing import Any, Dict, Sequence, Union

from mcp.types import EmbeddedResource, ImageContent, TextContent, Tool

from mcp_obsidian.tools.base import FileOperationToolHandler
from mcp_obsidian.utils.errors import ValidationError


class ReadNoteToolHandler(FileOperationToolHandler):
    """Tool handler for reading note content."""

    def __init__(self):
        """Initialize the tool handler."""
        super().__init__("obsidian_read_note")

    def get_tool_description(self) -> Tool:
        """Get the tool description for MCP."""
        return Tool(
            name=self.name,
            description="Get content of a note from your Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the note (relative to vault root)."
                    },
                    "format": {
                        "type": "string",
                        "description": "Format to return the content in (markdown or json).",
                        "enum": ["markdown", "json"],
                        "default": "markdown"
                    }
                },
                "required": ["path"]
            }
        )

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool arguments."""
        # Validate path
        filepath = self.validate_filepath(args.get("path"))
        
        # Validate format
        format = args.get("format", "markdown")
        if format not in ["markdown", "json"]:
            raise ValidationError(f"Invalid format: {format}. Must be 'markdown' or 'json'.")
        
        return {
            "path": filepath,
            "format": format
        }

    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments."""
        try:
            # Get file content
            content = self.obsidian_client.get_file_contents(
                filepath=args["path"],
                format=args["format"]
            )
            
            # Format response
            if args["format"] == "json":
                return [TextContent(
                    type="text",
                    text=json.dumps(content, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=content
                )]
        except Exception as e:
            return self.handle_error(e)


class CreateNoteToolHandler(FileOperationToolHandler):
    """Tool handler for creating or updating notes."""

    def __init__(self):
        """Initialize the tool handler."""
        super().__init__("obsidian_create_note")

    def get_tool_description(self) -> Tool:
        """Get the tool description for MCP."""
        return Tool(
            name=self.name,
            description="Create a new note or update an existing note in your Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the note (relative to vault root)."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the note."
                    }
                },
                "required": ["path", "content"]
            }
        )

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool arguments."""
        # Validate path
        filepath = self.validate_filepath(args.get("path"))
        
        # Validate content
        content = args.get("content")
        if not content:
            raise ValidationError("Content is required")
        
        return {
            "path": filepath,
            "content": content
        }

    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments."""
        try:
            # Create or update file
            self.obsidian_client.create_or_update_file(
                filepath=args["path"],
                content=args["content"]
            )
            
            return [TextContent(
                type="text",
                text=f"Successfully created/updated note at {args['path']}"
            )]
        except Exception as e:
            return self.handle_error(e)


class AppendNoteToolHandler(FileOperationToolHandler):
    """Tool handler for appending content to notes."""

    def __init__(self):
        """Initialize the tool handler."""
        super().__init__("obsidian_append_note")

    def get_tool_description(self) -> Tool:
        """Get the tool description for MCP."""
        return Tool(
            name=self.name,
            description="Append content to an existing note in your Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the note (relative to vault root)."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to append to the note."
                    }
                },
                "required": ["path", "content"]
            }
        )

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool arguments."""
        # Validate path
        filepath = self.validate_filepath(args.get("path"))
        
        # Validate content
        content = args.get("content")
        if not content:
            raise ValidationError("Content is required")
        
        return {
            "path": filepath,
            "content": content
        }

    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments."""
        try:
            # Append content to file
            self.obsidian_client.append_content(
                filepath=args["path"],
                content=args["content"]
            )
            
            return [TextContent(
                type="text",
                text=f"Successfully appended content to note at {args['path']}"
            )]
        except Exception as e:
            return self.handle_error(e)


class PatchNoteToolHandler(FileOperationToolHandler):
    """Tool handler for patching content at specific locations."""

    def __init__(self):
        """Initialize the tool handler."""
        super().__init__("obsidian_patch_note")

    def get_tool_description(self) -> Tool:
        """Get the tool description for MCP."""
        return Tool(
            name=self.name,
            description="Insert or modify content at a specific location in a note.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the note (relative to vault root)."
                    },
                    "operation": {
                        "type": "string",
                        "description": "Operation to perform.",
                        "enum": ["append", "prepend", "replace"],
                        "default": "append"
                    },
                    "target_type": {
                        "type": "string",
                        "description": "Type of target.",
                        "enum": ["heading", "block", "frontmatter"],
                        "default": "heading"
                    },
                    "target": {
                        "type": "string",
                        "description": "Target identifier (heading path, block reference, or frontmatter field)."
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to insert."
                    },
                    "create_target_if_missing": {
                        "type": "boolean",
                        "description": "Whether to create the target if it doesn't exist.",
                        "default": True
                    }
                },
                "required": ["path", "target", "content"]
            }
        )

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool arguments."""
        # Validate path
        filepath = self.validate_filepath(args.get("path"))
        
        # Validate operation
        operation = args.get("operation", "append")
        if operation not in ["append", "prepend", "replace"]:
            raise ValidationError(f"Invalid operation: {operation}. Must be 'append', 'prepend', or 'replace'.")
        
        # Validate target_type
        target_type = args.get("target_type", "heading")
        if target_type not in ["heading", "block", "frontmatter"]:
            raise ValidationError(f"Invalid target_type: {target_type}. Must be 'heading', 'block', or 'frontmatter'.")
        
        # Validate target
        target = args.get("target")
        if not target:
            raise ValidationError("Target is required")
        
        # Validate content
        content = args.get("content")
        if not content:
            raise ValidationError("Content is required")
        
        # Validate create_target_if_missing
        create_target_if_missing = args.get("create_target_if_missing", True)
        
        return {
            "path": filepath,
            "operation": operation,
            "target_type": target_type,
            "target": target,
            "content": content,
            "create_target_if_missing": create_target_if_missing
        }

    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments."""
        try:
            # Patch content
            self.obsidian_client.patch_content(
                filepath=args["path"],
                operation=args["operation"],
                target_type=args["target_type"],
                target=args["target"],
                content=args["content"],
                create_target_if_missing=args["create_target_if_missing"]
            )
            
            return [TextContent(
                type="text",
                text=f"Successfully patched content in note at {args['path']}"
            )]
        except Exception as e:
            return self.handle_error(e)


class DeleteNoteToolHandler(FileOperationToolHandler):
    """Tool handler for deleting notes."""

    def __init__(self):
        """Initialize the tool handler."""
        super().__init__("obsidian_delete_note")

    def get_tool_description(self) -> Tool:
        """Get the tool description for MCP."""
        return Tool(
            name=self.name,
            description="Delete a note from your Obsidian vault.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the note (relative to vault root)."
                    },
                    "confirm": {
                        "type": "boolean",
                        "description": "Confirmation to delete the note (must be true).",
                        "default": False
                    }
                },
                "required": ["path", "confirm"]
            }
        )

    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the tool arguments."""
        # Validate path
        filepath = self.validate_filepath(args.get("path"))
        
        # Validate confirm
        confirm = args.get("confirm", False)
        if not confirm:
            raise ValidationError("Confirm must be true to delete a note")
        
        return {
            "path": filepath,
            "confirm": confirm
        }

    def run_tool(self, args: Dict[str, Any]) -> Sequence[Union[TextContent, ImageContent, EmbeddedResource]]:
        """Execute the tool with the given arguments."""
        try:
            # Delete file
            self.obsidian_client.delete_file(filepath=args["path"])
            
            return [TextContent(
                type="text",
                text=f"Successfully deleted note at {args['path']}"
            )]
        except Exception as e:
            return self.handle_error(e)


# List of all file operation tool handlers
FILE_OPERATION_TOOLS = [
    ReadNoteToolHandler,
    CreateNoteToolHandler,
    AppendNoteToolHandler,
    PatchNoteToolHandler,
    DeleteNoteToolHandler
]
