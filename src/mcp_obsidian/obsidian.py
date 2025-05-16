"""
Obsidian API client for interacting with the Obsidian Local REST API.

This module provides a client for interacting with the Obsidian Local REST API,
which allows for reading and writing files in an Obsidian vault.
"""

import json
import urllib.parse
from typing import Any, Dict, List, Optional, Union

import requests
import yaml

from mcp_obsidian.config import ObsidianConfig, get_config
from mcp_obsidian.utils.errors import (
    AuthenticationError,
    ConnectionError,
    FileNotFoundError,
    ObsidianError,
    OperationNotSupportedError,
)


class ObsidianClient:
    """Client for interacting with the Obsidian Local REST API."""

    def __init__(self, config: Optional[ObsidianConfig] = None):
        """
        Initialize the Obsidian client with configuration.
        
        Args:
            config: Configuration for connecting to the Obsidian Local REST API.
                   If not provided, the global configuration will be used.
        """
        self.config = config or get_config().obsidian

    def get_base_url(self) -> str:
        """Get the base URL for the Obsidian Local REST API."""
        return self.config.get_base_url()

    def _get_headers(self) -> Dict[str, str]:
        """
        Generate headers with authentication.
        
        Returns:
            Dict containing headers with authentication.
        """
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "text/markdown",
        }

    def _safe_call(self, func: Any) -> Any:
        """
        Error handling wrapper for API calls.
        
        Args:
            func: Function to call.
            
        Returns:
            Result of the function call.
            
        Raises:
            AuthenticationError: If authentication fails.
            FileNotFoundError: If a file is not found.
            ConnectionError: If connection to the API fails.
            ObsidianError: For other API errors.
        """
        try:
            return func()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                raise AuthenticationError(
                    "Authentication failed. Check your API key."
                ) from e
            elif e.response.status_code == 404:
                # Extract path from URL if possible
                path = e.response.url.split("/vault/")[-1] if "/vault/" in e.response.url else "unknown"
                raise FileNotFoundError(path) from e
            
            # Try to parse error details from response
            try:
                error_data = e.response.json()
                message = error_data.get("message", str(e))
                error_code = error_data.get("errorCode", e.response.status_code)
            except (ValueError, KeyError):
                message = str(e)
                error_code = e.response.status_code
                
            raise ObsidianError(
                message=message,
                status_code=error_code,
            ) from e
        except requests.ConnectionError as e:
            raise ConnectionError(
                f"Failed to connect to Obsidian API at {self.get_base_url()}"
            ) from e
        except Exception as e:
            raise ObsidianError(f"Unexpected error: {str(e)}") from e

    # File Operations

    def get_file_contents(self, filepath: str, format: str = "markdown") -> str:
        """
        Get content of a file.
        
        Args:
            filepath: Path to the file relative to vault root.
            format: Format to return the content in. Either "markdown" or "json".
            
        Returns:
            Content of the file.
            
        Raises:
            FileNotFoundError: If the file is not found.
        """
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        headers = self._get_headers()
        if format == "json":
            headers["Accept"] = "application/vnd.olrapi.note+json"
        
        def call_fn():
            response = requests.get(
                url, 
                headers=headers, 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            if format == "json":
                return response.json()
            return response.text

        return self._safe_call(call_fn)

    def create_or_update_file(self, filepath: str, content: str) -> None:
        """
        Create or update a file.
        
        Args:
            filepath: Path to the file relative to vault root.
            content: Content to write to the file.
        """
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        def call_fn():
            response = requests.put(
                url, 
                headers=self._get_headers(), 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def append_content(self, filepath: str, content: str) -> None:
        """
        Append content to a file.
        
        Args:
            filepath: Path to the file relative to vault root.
            content: Content to append to the file.
        """
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        def call_fn():
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_content(
        self, 
        filepath: str, 
        operation: str, 
        target_type: str, 
        target: str, 
        content: str,
        create_target_if_missing: bool = True,
    ) -> None:
        """
        Insert content at specific location.
        
        Args:
            filepath: Path to the file relative to vault root.
            operation: Operation to perform. One of "append", "prepend", "replace".
            target_type: Type of target. One of "heading", "block", "frontmatter".
            target: Target identifier.
            content: Content to insert.
            create_target_if_missing: Whether to create the target if it doesn't exist.
        """
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        headers = self._get_headers()
        headers.update({
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
            "Create-Target-If-Missing": str(create_target_if_missing).lower(),
        })
        
        def call_fn():
            response = requests.patch(
                url, 
                headers=headers, 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_file(self, filepath: str) -> None:
        """
        Delete a file.
        
        Args:
            filepath: Path to the file relative to vault root.
        """
        url = f"{self.get_base_url()}/vault/{filepath}"
        
        def call_fn():
            response = requests.delete(
                url, 
                headers=self._get_headers(), 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    # Active File Operations

    def get_active_file(self, format: str = "markdown") -> Union[str, Dict[str, Any]]:
        """
        Get content of active file.
        
        Args:
            format: Format to return the content in. Either "markdown" or "json".
            
        Returns:
            Content of the active file.
        """
        url = f"{self.get_base_url()}/active/"
        
        headers = self._get_headers()
        if format == "json":
            headers["Accept"] = "application/vnd.olrapi.note+json"
        
        def call_fn():
            response = requests.get(
                url, 
                headers=headers, 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            if format == "json":
                return response.json()
            return response.text

        return self._safe_call(call_fn)

    def update_active_file(self, content: str) -> None:
        """
        Update active file.
        
        Args:
            content: Content to write to the file.
        """
        url = f"{self.get_base_url()}/active/"
        
        def call_fn():
            response = requests.put(
                url, 
                headers=self._get_headers(), 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def append_active_file(self, content: str) -> None:
        """
        Append to active file.
        
        Args:
            content: Content to append to the file.
        """
        url = f"{self.get_base_url()}/active/"
        
        def call_fn():
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def patch_active_file(
        self, 
        operation: str, 
        target_type: str, 
        target: str, 
        content: str,
        create_target_if_missing: bool = True,
    ) -> None:
        """
        Insert content at location in active file.
        
        Args:
            operation: Operation to perform. One of "append", "prepend", "replace".
            target_type: Type of target. One of "heading", "block", "frontmatter".
            target: Target identifier.
            content: Content to insert.
            create_target_if_missing: Whether to create the target if it doesn't exist.
        """
        url = f"{self.get_base_url()}/active/"
        
        headers = self._get_headers()
        headers.update({
            "Operation": operation,
            "Target-Type": target_type,
            "Target": urllib.parse.quote(target),
            "Create-Target-If-Missing": str(create_target_if_missing).lower(),
        })
        
        def call_fn():
            response = requests.patch(
                url, 
                headers=headers, 
                data=content,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def delete_active_file(self) -> None:
        """Delete active file."""
        url = f"{self.get_base_url()}/active/"
        
        def call_fn():
            response = requests.delete(
                url, 
                headers=self._get_headers(), 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    def show_file(self, filepath: str, new_leaf: bool = False) -> None:
        """
        Open file in Obsidian UI.
        
        Args:
            filepath: Path to the file relative to vault root.
            new_leaf: Whether to open the file in a new leaf.
        """
        query = "?newLeaf=true" if new_leaf else ""
        url = f"{self.get_base_url()}/open/{urllib.parse.quote(filepath)}{query}"
        
        def call_fn():
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return None

        return self._safe_call(call_fn)

    # Folder Operations

    def list_files_in_vault(self) -> List[Dict[str, Any]]:
        """
        List files in vault root.
        
        Returns:
            List of files in the vault root.
        """
        url = f"{self.get_base_url()}/vault/"
        
        def call_fn():
            response = requests.get(
                url, 
                headers=self._get_headers(), 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["files"]

        return self._safe_call(call_fn)

    def list_files_in_dir(self, dirpath: str) -> List[Dict[str, Any]]:
        """
        List files in specific directory.
        
        Args:
            dirpath: Path to the directory relative to vault root.
            
        Returns:
            List of files in the directory.
        """
        url = f"{self.get_base_url()}/vault/{dirpath}/"
        
        def call_fn():
            response = requests.get(
                url, 
                headers=self._get_headers(), 
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            return response.json()["files"]

        return self._safe_call(call_fn)

    # Search Operations

    def search(self, query: str, context_length: int = 100) -> List[Dict[str, Any]]:
        """
        Simple text search.
        
        Args:
            query: Text to search for.
            context_length: Length of context to include around matches.
            
        Returns:
            List of search results.
        """
        url = f"{self.get_base_url()}/search/simple/"
        params = {
            "query": query,
            "contextLength": context_length
        }
        
        def call_fn():
            response = requests.post(
                url, 
                headers=self._get_headers(), 
                params=params,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def search_json(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Advanced search with JSON Logic.
        
        Args:
            query: JSON Logic query.
            
        Returns:
            List of search results.
        """
        url = f"{self.get_base_url()}/search/"
        
        headers = self._get_headers()
        headers["Content-Type"] = "application/vnd.olrapi.jsonlogic+json"
        
        def call_fn():
            response = requests.post(
                url, 
                headers=headers, 
                json=query,
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    def search_dql(self, query: str) -> List[Dict[str, Any]]:
        """
        Search using Dataview Query Language.
        
        Args:
            query: Dataview Query Language query.
            
        Returns:
            List of search results.
        """
        url = f"{self.get_base_url()}/search/"
        
        headers = self._get_headers()
        headers["Content-Type"] = "application/vnd.olrapi.dataview.dql+txt"
        
        def call_fn():
            response = requests.post(
                url, 
                headers=headers, 
                data=query.encode("utf-8"),
                verify=self.config.verify_ssl, 
                timeout=self.config.timeout
            )
            response.raise_for_status()
            return response.json()

        return self._safe_call(call_fn)

    # Utility Methods

    def parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """
        Parse YAML frontmatter from content.
        
        Args:
            content: Content to parse frontmatter from.
            
        Returns:
            Dictionary containing frontmatter properties.
        """
        if not content.startswith("---"):
            return {}
        
        try:
            # Find the end of the frontmatter
            end_index = content.find("---", 3)
            if end_index == -1:
                return {}
            
            # Extract and parse the frontmatter
            frontmatter_text = content[3:end_index].strip()
            return yaml.safe_load(frontmatter_text) or {}
        except Exception:
            return {}

    def get_batch_file_contents(self, filepaths: List[str]) -> str:
        """
        Get contents of multiple files and concatenate them with headers.
        
        Args:
            filepaths: List of file paths to read.
            
        Returns:
            String containing all file contents with headers.
        """
        result = []
        
        for filepath in filepaths:
            try:
                content = self.get_file_contents(filepath)
                result.append(f"# {filepath}\n\n{content}\n\n---\n\n")
            except Exception as e:
                # Add error message but continue processing other files
                result.append(f"# {filepath}\n\nError reading file: {str(e)}\n\n---\n\n")
                
        return "".join(result)
