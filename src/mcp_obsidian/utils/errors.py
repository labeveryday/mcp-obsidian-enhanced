"""
Error handling utilities for the Obsidian MCP server.

This module defines custom exception classes and error formatting functions.
"""

from typing import Any, Dict, Optional


class ObsidianError(Exception):
    """Base class for Obsidian API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(ObsidianError):
    """Raised when authentication with the Obsidian API fails."""

    def __init__(self, message: str = "Authentication failed", **kwargs: Any):
        super().__init__(message, status_code=401, **kwargs)


class ConnectionError(ObsidianError):
    """Raised when connection to the Obsidian API fails."""

    def __init__(self, message: str = "Failed to connect to Obsidian API", **kwargs: Any):
        super().__init__(message, **kwargs)


class FileNotFoundError(ObsidianError):
    """Raised when a file is not found in the vault."""

    def __init__(self, path: str, **kwargs: Any):
        super().__init__(f"File not found: {path}", status_code=404, **kwargs)


class ValidationError(ObsidianError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Validation failed", **kwargs: Any):
        super().__init__(message, status_code=400, **kwargs)


class PluginNotAvailableError(ObsidianError):
    """Raised when a required plugin is not available."""

    def __init__(self, plugin_name: str, **kwargs: Any):
        super().__init__(
            f"Required plugin '{plugin_name}' is not available", 
            status_code=501, 
            **kwargs
        )


class OperationNotSupportedError(ObsidianError):
    """Raised when an operation is not supported."""

    def __init__(self, operation: str, **kwargs: Any):
        super().__init__(
            f"Operation not supported: {operation}", 
            status_code=501, 
            **kwargs
        )


def format_error_for_mcp(error: Exception) -> Dict[str, Any]:
    """
    Format an error for MCP response.
    
    Args:
        error: The exception to format
        
    Returns:
        Dict containing formatted error information
    """
    if isinstance(error, ObsidianError):
        status_code = error.status_code or 500
        details = error.details
    else:
        status_code = 500
        details = {}
    
    return {
        "error": {
            "message": str(error),
            "type": error.__class__.__name__,
            "status_code": status_code,
            "details": details,
        }
    }
