"""Custom exceptions for the Obsidian MCP server."""


class ObsidianError(Exception):
    """Base exception for all Obsidian-related errors."""
    pass


class ObsidianConnectionError(ObsidianError):
    """Error connecting to the Obsidian API."""
    pass


class ObsidianAPIError(ObsidianError):
    """Error from the Obsidian API."""
    pass


class ObsidianNotFoundError(ObsidianAPIError):
    """Resource not found in Obsidian."""
    pass


class ConfigurationError(Exception):
    """Error in the configuration."""
    pass
