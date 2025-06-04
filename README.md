# Obsidian MCP Server Enhanced

![Status: Phase 1 Complete](https://img.shields.io/badge/status-Phase%201%20Complete-brightgreen)

A Model Context Protocol (MCP) server for integrating Amazon Q with Obsidian.

## Project Overview

This MCP server allows Amazon Q to interact with Obsidian vaults without requiring the Obsidian application to be open. It leverages the Obsidian [Local REST API plugin](https://coddingtonbear.github.io/obsidian-local-rest-api/) to provide functionality for note management, search, and knowledge management.

## Current Status

- **Phase 1 (Core Infrastructure)**: Complete
- Basic file operations, search, and note templates are fully implemented
- Built with FastMCP for seamless integration with Amazon Q
- Uses decorator-based approach for prompt registration
- Ready to begin Phase 2: Essential Features

## Features

### Currently Implemented

- **File Operations**: Read, create, update, append to, and delete notes
- **Basic Folder Management**: List files in folders
- **Search**: Basic search functionality for notes
- **Daily Notes**: Create daily notes with predefined sections
- **Meeting Notes**: Create meeting notes with structured templates

### Planned Features

- **Advanced Folder Management**: Create, delete, rename, and move folders
- **Organization & Metadata**: Manage tags, frontmatter, and file organization
- **Advanced Search & Discovery**: Enhanced search by content, tags, and other criteria
- **Knowledge Management**: Extract highlights, compile notes, and more
- **Search and Compile**: Search for notes and compile information into a single note
- **Note Organization**: Organize notes on specific topics with AI assistance

## Getting Started

### Prerequisites

1. **Obsidian**: Install [Obsidian](https://obsidian.md/) and create a vault
2. **Local REST API Plugin**: Install the [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin in Obsidian
3. **Python 3.10+**: Make sure you have Python 3.10 or newer installed

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/mcp-obsidian-enhanced.git
   cd mcp-obsidian-enhanced
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Create a `.env` file with your Obsidian API configuration:
   ```
   OBSIDIAN_API_KEY=your_api_key_from_local_rest_api_plugin
   OBSIDIAN_HOST=127.0.0.1
   OBSIDIAN_PORT=27124
   ```

### Integration with Amazon Q CLI

To integrate this MCP server with Amazon Q CLI, configure the MCP server in your AWS configuration:

1. Create or update the file at `~/.aws/amazonq/mcp.json`:

```json
{
  "mcpServers": {
    "obsidian-mcp-server": {
        "command": "uv",
        "args": ["--directory", "/path/to/mcp-obsidian-enhanced", "run", "run_server.py"],
        "env": {},
        "disabled": false,
        "autoApprove": []
    }
  }
}
```

2. Replace `/path/to/mcp-obsidian-enhanced` with the actual path to your repository.

### Running the Server

Run the server with:

```bash
python run_server.py
```

To test with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory ./ "run" "run_server.py"
```

## Available Tools

| Tool Name | Description |
|-----------|-------------|
| `obsidian_read_note` | Get content of a note from your Obsidian vault |
| `obsidian_create_note` | Create a new note in your Obsidian vault |
| `obsidian_update_note` | Update an existing note in your Obsidian vault |
| `obsidian_append_note` | Append content to an existing note |
| `obsidian_delete_note` | Delete a note from your Obsidian vault |
| `obsidian_list_files` | List files and folders in your Obsidian vault |
| `obsidian_get_active_file` | Get the currently active file in Obsidian |
| `obsidian_create_daily_note` | Create a daily note with predefined sections |

### Planned Tools (Phase 2)
| Tool Name | Description |
|-----------|-------------|
| `obsidian_search` | Search for notes in your Obsidian vault |
| `obsidian_summarize_note` | Summarize the content of a note |
| `obsidian_search_and_compile` | Search for notes and compile information |
| `obsidian_organize_notes` | Organize notes on a specific topic |

## Available Prompts

The server provides prompt templates using the decorator-based approach:

### Meeting Notes

```python
@mcp.prompt("meeting-notes")
async def meeting_notes_prompt(
    title: str,
    date: str = "",
    participants: str = "",
    folder: str = "Meetings",
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create a meeting note with the given details."""
    # Implementation...
```

### Create Note

```python
@mcp.prompt("create-note")
async def create_note_prompt(
    title: str,
    content: str,
    folder: str = "",
    tags: List[str] = None
) -> Dict[str, Any]:
    """Create a new note with the given details."""
    # Implementation...
```

### Organize Notes

```python
@mcp.prompt("organize-notes")
async def organize_notes_prompt(
    topic: str,
    folder: str = ""
) -> Dict[str, Any]:
    """Organize notes related to a specific topic."""
    # Implementation...
```

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OBSIDIAN_API_KEY` | API key from Local REST API plugin | (Required) |
| `OBSIDIAN_HOST` | Host where Obsidian is running | 127.0.0.1 |
| `OBSIDIAN_PORT` | Port for the API | 27124 |
| `OBSIDIAN_PROTOCOL` | Protocol to use | https |
| `OBSIDIAN_VERIFY_SSL` | Whether to verify SSL certificates | false |
| `OBSIDIAN_TIMEOUT` | Connection timeout in seconds | 10 |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | INFO |

## Implementation Roadmap

### Phase 1: Core Infrastructure (Complete)
- ✅ Basic server setup with FastMCP
- ✅ Configuration management
- ✅ Obsidian API client
- ✅ Basic file operations
- ✅ Basic folder management tools

### Phase 2: Essential Features (Planned)
- Advanced search functionality
- Metadata management
- Improved templates
- Note organization capabilities
- Search and compile functionality
- Note summarization

### Phase 3: Advanced Features (Planned)
- Knowledge management tools
- Bulk operations
- Advanced search capabilities

### Phase 4: Optimization & Polish (Planned)
- Performance optimizations
- Enhanced error handling
- Comprehensive logging
- Detailed documentation

## Testing the API Directly

You can test the Obsidian Local REST API endpoints directly using curl:

### List Files in a Folder
```bash
curl -X GET "http://127.0.0.1:27124/vault/FolderName?list=true" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Read a Note
```bash
curl -X GET "http://127.0.0.1:27124/vault/path/to/note.md" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Create/Update a Note
```bash
curl -X PUT "http://127.0.0.1:27124/vault/path/to/note.md" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: text/markdown" \
  -d "# Note Title\n\nNote content here."
```

### Search Notes
```bash
curl -X POST "http://127.0.0.1:27124/search/simple" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=search_term"
```

## Contributing

Contributions are welcome! Please see the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
