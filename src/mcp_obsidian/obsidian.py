"""Obsidian API client for interacting with the Local REST API."""

import json
import logging
from typing import Dict, Any, List, Optional

import httpx

from mcp_obsidian.config import ObsidianConfig
from mcp_obsidian.utils.errors import (
    ObsidianAPIError,
    ObsidianConnectionError,
    ObsidianNotFoundError
)

# Set up logger
logger = logging.getLogger(__name__)

class ObsidianClient:
    """Client for interacting with Obsidian Local REST API."""
    
    def __init__(self, config: ObsidianConfig):
        """Initialize the Obsidian API client.
        
        Args:
            config: Configuration for the Obsidian API
        """
        self.config = config
        self.base_url = f"{config.protocol}://{config.host}:{config.port}"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "text/markdown"
        }
        self.client = None
        logger.info(f"Initialized ObsidianClient with base URL: {self.base_url}")
    
    async def connect(self) -> bool:
        """Test connection to Obsidian API.
        
        Returns:
            bool: True if connection successful, False otherwise
        
        Raises:
            ObsidianConnectionError: If connection fails
        """
        self.client = httpx.AsyncClient(verify=self.config.verify_ssl, timeout=self.config.timeout)
        try:
            logger.debug(f"Attempting to connect to {self.base_url}/")
            response = await self.client.get(f"{self.base_url}/", headers=self.headers)
            logger.debug(f"Connection response status: {response.status_code}")
            return response.status_code == 200
        except httpx.RequestError as e:
            logger.error(f"Connection error: {str(e)}")
            raise ObsidianConnectionError(f"Failed to connect to Obsidian API: {str(e)}")
    
    async def close(self):
        """Close the client connection."""
        if self.client:
            await self.client.aclose()
    
    async def get_note_content(self, path: str, include_metadata: bool = False) -> str:
        """Get content of a note.
        
        Args:
            path: Path to the note (relative to vault root)
            include_metadata: Whether to include frontmatter metadata
            
        Returns:
            str: Content of the note
            
        Raises:
            ObsidianNotFoundError: If the note doesn't exist
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            response = await self.client.get(
                f"{self.base_url}/vault/{path}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                raise ObsidianNotFoundError(f"Note not found: {path}")
            
            response.raise_for_status()
            content = response.text
            
            if not include_metadata and content.startswith("---"):
                # Strip frontmatter if not requested
                end_marker = content.find("---", 3)
                if end_marker > 0:
                    content = content[end_marker + 3:].strip()
            
            return content
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def create_note(
        self, 
        path: str, 
        content: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Create a new note.
        
        Args:
            path: Path where to create the note (relative to vault root)
            content: Content of the note
            metadata: Optional frontmatter metadata to include
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            logger.debug("Client not initialized, connecting...")
            await self.connect()
            
        if metadata:
            # Add frontmatter if metadata provided
            frontmatter = "---\n" + "\n".join([f"{k}: {json.dumps(v)}" for k, v in metadata.items()]) + "\n---\n\n"
            content = frontmatter + content
        
        url = f"{self.base_url}/vault/{path}"
        logger.debug(f"Creating note at {url}")
        logger.debug(f"Request headers: {self.headers}")
        logger.debug(f"Content length: {len(content)}")
        
        try:
            response = await self.client.put(
                url,
                headers=self.headers,
                content=content
            )
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            if response.status_code != 200:
                logger.error(f"Response content: {response.text}")
            response.raise_for_status()
            return response.status_code in (200, 201, 204)
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {str(e)}")
            logger.error(f"Response content: {e.response.text if hasattr(e, 'response') else 'No response content'}")
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise ObsidianAPIError(f"Unexpected error: {str(e)}")
    
    async def update_note(self, path: str, content: str) -> bool:
        """Update an existing note.
        
        Args:
            path: Path to the note (relative to vault root)
            content: New content for the note
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ObsidianNotFoundError: If the note doesn't exist
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            # First check if the note exists
            await self.get_note_content(path)
            
            # Then update it
            response = await self.client.put(
                f"{self.base_url}/vault/{path}",
                headers=self.headers,
                content=content
            )
            response.raise_for_status()
            return response.status_code in (200, 201, 204)
            
        except ObsidianNotFoundError:
            raise
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def append_to_note(self, path: str, content: str) -> bool:
        """Append content to an existing note.
        
        Args:
            path: Path to the note (relative to vault root)
            content: Content to append
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ObsidianNotFoundError: If the note doesn't exist
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            # Get existing content
            existing_content = await self.get_note_content(path, include_metadata=True)
            
            # Append new content
            new_content = existing_content + "\n\n" + content
            
            # Update the note
            return await self.update_note(path, new_content)
            
        except ObsidianNotFoundError:
            raise
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def delete_note(self, path: str) -> bool:
        """Delete a note.
        
        Args:
            path: Path to the note (relative to vault root)
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ObsidianNotFoundError: If the note doesn't exist
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            response = await self.client.delete(
                f"{self.base_url}/vault/{path}",
                headers=self.headers
            )
            
            if response.status_code == 404:
                raise ObsidianNotFoundError(f"Note not found: {path}")
                
            response.raise_for_status()
            return response.status_code in (200, 204)
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def list_files(self, folder: str = "") -> List[Dict[str, Any]]:
        """List files in a folder.
        
        Args:
            folder: Folder path (relative to vault root)
            
        Returns:
            List[Dict[str, Any]]: List of files with metadata
            
        Raises:
            ObsidianNotFoundError: If the folder doesn't exist
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            response = await self.client.get(
                f"{self.base_url}/vault/{folder}",
                headers=self.headers,
                params={"list": True}
            )
            
            if response.status_code == 404:
                raise ObsidianNotFoundError(f"Folder not found: {folder}")
                
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def search(self, query: str, query_format: str = "dataview") -> List[Dict[str, Any]]:
        """Search for notes using Dataview or JsonLogic queries.
        
        Args:
            query: Search query in Dataview DQL or JsonLogic format
            query_format: Query format to use ("dataview" or "jsonlogic")
            
        Returns:
            List[Dict[str, Any]]: List of matching notes with metadata
            
        Raises:
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        # Set content type based on query format
        if query_format == "dataview":
            content_type = "application/vnd.olrapi.dataview.dql+txt"
        elif query_format == "jsonlogic":
            content_type = "application/vnd.olrapi.jsonlogic+json"
        else:
            raise ValueError(f"Unsupported query format: {query_format}")
            
        headers = {
            **self.headers,
            "Content-Type": content_type
        }
            
        try:
            response = await self.client.post(
                f"{self.base_url}/search",
                headers=headers,
                content=query
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
            
    async def simple_search(self, query: str, context_length: int = 100) -> List[Dict[str, Any]]:
        """Search for notes using simple text search.
        
        Args:
            query: Text to search for
            context_length: How much context to return around the matching string (default: 100)
            
        Returns:
            List[Dict[str, Any]]: List of matching notes with metadata and context
            
        Raises:
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            # Set proper headers for form data
            headers = {
                **self.headers,
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # Send query as form data
            response = await self.client.post(
                f"{self.base_url}/search/simple",
                headers=headers,
                data={
                    "query": query,
                    "contextLength": context_length
                }
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
    
    async def get_active_file(self) -> Dict[str, Any]:
        """Get information about the currently active file.
        
        Returns:
            Dict[str, Any]: Information about the active file
            
        Raises:
            ObsidianAPIError: If the API request fails
        """
        if not self.client:
            await self.connect()
            
        try:
            response = await self.client.get(
                f"{self.base_url}/active-file",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            raise ObsidianAPIError(f"API error: {str(e)}")
        except httpx.RequestError as e:
            raise ObsidianConnectionError(f"Connection error: {str(e)}")
