# Obsidian MCP Server Enhanced

![Status: Phase 1 Complete](https://img.shields.io/badge/status-Phase%201%20Complete-brightgreen)

A Model Context Protocol (MCP) server for integrating Amazon Q with Obsidian.

---

**Project Status:**
- **Phase 1 (Core Infrastructure) is now complete.**
- The server supports FastMCP, configuration management, an async Obsidian API client, and all basic file operations.
- The codebase has been refactored to use explicit `@mcp.prompt` decorators for prompt registration, matching the FastMCP SDK and best practices.
- Ready to begin Phase 2: Essential Features.

---

## Project Overview

This MCP server allows Amazon Q to interact with Obsidian vaults without requiring the Obsidian application to be open. It leverages the Obsidian Local REST API plugin to provide a wide range of functionality for note management, organization, search, and knowledge management.

## Features

- **File Operations**: Read, create, update, append to, and delete notes
- **Folder Management**: List, create, delete, rename, and move folders
- **Organization & Metadata**: Manage tags, frontmatter, and file organization
- **Search & Discovery**: Search notes by content, tags, and other criteria
- **Knowledge Management**: Work with daily notes, extract highlights, and more

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

### Running the Server

Run the server with:

```bash
python run_server.py
```

To test with MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory ./ "run_server.py"
```

## Implementation Details

### Architecture

This project uses FastMCP, a modern approach for building MCP servers in Python. Key components include:

1. **ObsidianClient**: Wrapper around the Obsidian Local REST API
2. **MCP Server**: FastMCP implementation with tools, resources, and prompts
3. **Configuration**: Environment-based configuration management

### Available Tools

| Category | Tools |
|----------|-------|
| File Operations | `obsidian_read_note`, `obsidian_create_note`, `obsidian_update_note`, `obsidian_append_note`, `obsidian_delete_note` |
| Folder Management | `obsidian_list_files` |
| Search | `obsidian_search` |
| Active File | `obsidian_get_active_file` |

### Resources

Notes in the Obsidian vault are exposed as resources with URIs in the format:
```
obsidian://path/to/note.md
```

### Prompts

The server provides prompt templates for common operations:
- `create-daily-note`: Create a daily note with template
- `search-notes`: Search notes with specific criteria

## Using Prompts

The MCP server provides several prompt templates to help you create and manage notes in your Obsidian vault. These prompts make it easy to create structured notes with consistent formatting.

**Note:** Prompts are now registered explicitly using `@mcp.prompt("name")` decorators. Dynamic prompt execution (e.g., `mcp.execute_prompt`) is no longer used. See the codebase for examples of prompt registration.

### Available Prompts

1. **Create Note** (`create-note`)
   ```python
   await mcp.execute_prompt("create-note", {
       "title": "Project Ideas",
       "folder": "Projects/",
       "template": "project",
       "tags": "project, ideas"
   })
   ```

2. **Meeting Notes** (`meeting-notes`)
   ```python
   await mcp.execute_prompt("meeting-notes", {
       "title": "Team Sync",
       "date": "2024-03-20",
       "participants": "John, Jane, Bob",
       "folder": "Meetings/"
   })
   ```

3. **Project Notes** (`project-notes`)
   ```python
   await mcp.execute_prompt("project-notes", {
       "title": "Website Redesign",
       "status": "in-progress",
       "priority": "high",
       "folder": "Projects/"
   })
   ```

4. **Daily Notes** (`daily-notes`)
   ```python
   await mcp.execute_prompt("daily-notes", {
       "date": "2024-03-20",
       "folder": "Daily Notes/",
       "tags": "daily, work"
   })
   ```

5. **Search and Compile** (`search-compile`)
   ```python
   await mcp.execute_prompt("search-compile", {
       "query": "tag:#project",
       "output_path": "Compiled/Projects.md",
       "format": "detailed"
   })
   ```

6. **Note Summary** (`note-summary`)
   ```python
   await mcp.execute_prompt("note-summary", {
       "path": "Projects/Website.md",
       "length": "medium",
       "include_metadata": true
   })
   ```

7. **Organize Notes** (`organize-notes`)
   ```python
   await mcp.execute_prompt("organize-notes", {
       "topic": "project management",
       "folder": "Projects/",
       "structure": "hierarchical"
   })
   ```

### Using Prompts with curl

You can also use prompts directly with curl commands:

```bash
# Create a meeting note
curl -X POST "http://127.0.0.1:27124/prompts/execute" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "meeting-notes",
    "arguments": {
      "title": "Team Sync",
      "date": "2024-03-20",
      "participants": "John, Jane, Bob",
      "folder": "Meetings/"
    }
  }'

# Create a daily note
curl -X POST "http://127.0.0.1:27124/prompts/execute" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "daily-notes",
    "arguments": {
      "date": "2024-03-20",
      "folder": "Daily Notes/",
      "tags": "daily, work"
    }
  }'
```

### Prompt Templates

Each prompt template includes:

- Required and optional arguments
- Default values where applicable
- Clear descriptions of each parameter
- Support for common use cases

The templates are designed to work with your existing tools and provide a more structured way to interact with your Obsidian vault.

## Development

### Project Structure

```
mcp-obsidian/
├── src/
│   └── mcp_obsidian/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       ├── obsidian.py       # Obsidian API client
│       ├── server.py         # MCP server implementation
│       └── utils/
│           ├── __init__.py
│           └── errors.py     # Custom exceptions
├── pyproject.toml            # Project configuration
├── README.md
└── run_server.py             # Server entry point
```

### Implementation Phases

#### Phase 1: Core Infrastructure (**Complete**)
- Basic server setup with FastMCP
- Configuration management
- Obsidian API client
- Basic file operations

#### Phase 2: Essential Features (Next)
- Folder management tools
- Advanced search functionality
- Metadata management
- Subscription support

#### Phase 3: Advanced Features
- Knowledge management tools
- Bulk operations
- Template support
- Advanced search capabilities

#### Phase 4: Optimization & Polish
- Performance optimizations
- Enhanced error handling
- Comprehensive logging
- Detailed documentation

## Configuration Options

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `OBSIDIAN_API_KEY` | API key from Local REST API plugin | (Required) |
| `OBSIDIAN_HOST` | Host where Obsidian is running | 127.0.0.1 |
| `OBSIDIAN_PORT` | Port for the API | 27124 |
| `OBSIDIAN_PROTOCOL` | Protocol to use | http |
| `OBSIDIAN_VERIFY_SSL` | Whether to verify SSL certificates | false |
| `OBSIDIAN_TIMEOUT` | Connection timeout in seconds | 10 |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, etc.) | INFO |

## API Testing with curl

You can test the Obsidian Local REST API endpoints directly using curl. Replace `YOUR_API_KEY` with your actual API key from the Local REST API plugin settings.

### File Operations

#### Create/Update a Note
```bash
# Create or update a note
curl -X PUT "http://127.0.0.1:27124/vault/AWS-Training/test.md" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: text/markdown" \
  -d "# Test Note

This is a test note with a tag.

---
tags: [test]
---"
```

#### Read a Note
```bash
# Read a note
curl -X GET "http://127.0.0.1:27124/vault/AWS-Training/test.md" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

#### Delete a Note
```bash
# Delete a note
curl -X DELETE "http://127.0.0.1:27124/vault/AWS-Training/test.md" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Folder Operations

#### List Files
```bash
# List files in a folder
curl -X GET "http://127.0.0.1:27124/vault/AWS-Training?list=true" \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### Search Operations

#### Simple Text Search
The simple search endpoint searches across your entire vault by default. You can use search operators to narrow down results:

- `path:folder/` - Search only in a specific folder
- `tag:#tag` - Search for notes with specific tags
- `file:name.md` - Search for specific filenames
- `content:"text"` - Search for specific content

```bash
# Search across entire vault
curl -X POST "http://127.0.0.1:27124/search/simple" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=your+search+text"

# Search in specific folder
curl -X POST "http://127.0.0.1:27124/search/simple" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=path:AWS-Training+your+search+text"

# Search with custom context length
curl -X POST "http://127.0.0.1:27124/search/simple" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "query=your+search+text&contextLength=200"
```

#### Advanced Search (Dataview/JsonLogic)
For more complex searches, you can use Dataview or JsonLogic queries:

```bash
# Search using Dataview query
curl -X POST "http://127.0.0.1:27124/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/vnd.olrapi.dataview.dql+txt" \
  -d "TABLE file.name, file.mtime FROM #project"

# Search using JsonLogic query
curl -X POST "http://127.0.0.1:27124/search" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/vnd.olrapi.jsonlogic+json" \
  -d '{"glob": ["*.md", "file.path"]}'
```

### Testing Notes

1. Make sure Obsidian is running and the Local REST API plugin is enabled
2. Replace `YOUR_API_KEY` with your actual API key
3. All paths are relative to your vault root
4. The API returns JSON responses for most operations

Example response formats:

#### Successful Response
```json
{
  "status": "success",
  "data": {
    "content": "# Note Content\n\nThis is the note content.",
    "metadata": {
      "tags": ["test"],
      "date": "2024-03-20"
    }
  }
}
```

#### Error Response
```json
{
  "status": "error",
  "error": {
    "code": "not_found",
    "message": "Note not found: test.md"
  }
}
```

### Common Issues and Solutions

1. **Path Issues**
   - Use forward slashes (/) for paths
   - Paths are case-sensitive
   - Always include the .md extension for files

2. **Content-Type Issues**
   - Use `text/markdown` for note content
   - Use `application/json` for API responses

3. **Authentication Issues**
   - Make sure the API key is correct
   - Check that the Bearer token format is correct
   - Verify the API key is enabled in the Local REST API plugin settings

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
