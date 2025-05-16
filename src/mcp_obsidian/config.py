"""
Configuration management for the Obsidian MCP server.

This module handles loading and validating configuration from environment variables
and provides access to configuration values throughout the application.
"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class ObsidianConfig:
    """Configuration for connecting to the Obsidian Local REST API."""

    api_key: str
    host: str = "127.0.0.1"
    port: int = 27124
    protocol: str = "https"
    verify_ssl: bool = False
    timeout: int = 10
    smart_connections_enabled: bool = False
    templater_enabled: bool = False

    def get_base_url(self) -> str:
        """Get the base URL for the Obsidian Local REST API."""
        return f"{self.protocol}://{self.host}:{self.port}"


@dataclass
class Config:
    """Global configuration for the MCP server."""

    obsidian: ObsidianConfig
    debug: bool = False
    log_level: str = "INFO"


def load_config() -> Config:
    """
    Load configuration from environment variables.
    
    Returns:
        Config: The loaded configuration.
        
    Raises:
        ValueError: If required configuration values are missing.
    """
    # Load environment variables from .env file if it exists
    load_dotenv()

    # Required configuration
    api_key = os.getenv("OBSIDIAN_API_KEY")
    if not api_key:
        raise ValueError("OBSIDIAN_API_KEY environment variable is required")

    # Optional configuration with defaults
    host = os.getenv("OBSIDIAN_HOST", "127.0.0.1")
    port = int(os.getenv("OBSIDIAN_PORT", "27124"))
    protocol = os.getenv("OBSIDIAN_PROTOCOL", "https")
    verify_ssl = os.getenv("OBSIDIAN_VERIFY_SSL", "false").lower() == "true"
    timeout = int(os.getenv("OBSIDIAN_TIMEOUT", "10"))
    smart_connections_enabled = os.getenv("OBSIDIAN_SMART_CONNECTIONS_ENABLED", "false").lower() == "true"
    templater_enabled = os.getenv("OBSIDIAN_TEMPLATER_ENABLED", "false").lower() == "true"
    debug = os.getenv("DEBUG", "false").lower() == "true"
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    obsidian_config = ObsidianConfig(
        api_key=api_key,
        host=host,
        port=port,
        protocol=protocol,
        verify_ssl=verify_ssl,
        timeout=timeout,
        smart_connections_enabled=smart_connections_enabled,
        templater_enabled=templater_enabled,
    )

    return Config(
        obsidian=obsidian_config,
        debug=debug,
        log_level=log_level,
    )


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Returns:
        Config: The global configuration instance.
    """
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config
    _config = None
