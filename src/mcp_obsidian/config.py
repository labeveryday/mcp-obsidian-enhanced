"""Configuration management for the Obsidian MCP server."""

import os
from dataclasses import dataclass
from typing import Optional

# Load environment variables from .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


@dataclass
class ObsidianConfig:
    """Configuration for connecting to Obsidian Local REST API."""
    
    api_key: str
    host: str = "127.0.0.1"
    port: int = 27124
    protocol: str = "https"
    verify_ssl: bool = False
    timeout: int = 10


def load_config() -> ObsidianConfig:
    """Load configuration from environment variables.
    
    Returns:
        ObsidianConfig: Configuration for Obsidian API
    """
    return ObsidianConfig(
        api_key=os.environ.get("OBSIDIAN_API_KEY", ""),
        host=os.environ.get("OBSIDIAN_HOST", "127.0.0.1"),
        port=int(os.environ.get("OBSIDIAN_PORT", "27124")),
        protocol=os.environ.get("OBSIDIAN_PROTOCOL", "https"),
        verify_ssl=os.environ.get("OBSIDIAN_VERIFY_SSL", "").lower() in ("true", "1", "yes"),
        timeout=int(os.environ.get("OBSIDIAN_TIMEOUT", "10"))
    )
