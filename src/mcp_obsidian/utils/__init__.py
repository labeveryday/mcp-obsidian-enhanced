"""Utility functions and classes for the Obsidian MCP server."""

from mcp_obsidian.utils.errors import (
    ObsidianError,
    ObsidianConnectionError,
    ObsidianAPIError,
    ObsidianNotFoundError,
    ConfigurationError
)

__all__ = [
    "ObsidianError",
    "ObsidianConnectionError",
    "ObsidianAPIError",
    "ObsidianNotFoundError",
    "ConfigurationError"
]
