# Obsidian MCP Server Documentation

## Running the Server

You can run the MCP server in several ways:

### 1. Using the installed package

After installing the package, you can run the server using the entry point script:

```bash
mcp-obsidian
```

### 2. Using the Python module

You can run the server directly as a Python module:

```bash
python -m mcp_obsidian
```

### 3. Using the run script

For quick testing, you can use the provided run script:

```bash
python run_server.py
```

## Testing with MCP Inspector

The MCP Inspector is a tool for testing MCP servers. You can use it to test the Obsidian MCP server:

### Installation

```bash
# Install the MCP Inspector globally
npm install -g @modelcontextprotocol/inspector
```

### Running the Inspector

```bash
# Run the inspector with the server
npx @modelcontextprotocol/inspector \
  uv \
  --directory /path/to/mcp-obsidian-enhanced \
  run \
  mcp_obsidian
```

This will start the MCP Inspector and connect it to the Obsidian MCP server, allowing you to test the available tools.

## Available Tools

### File Operations

- **obsidian_read_note**
  - Description: Get content of a note from your Obsidian vault
  - Parameters:
    - `path` (string, required): Path to the note (relative to vault root)
    - `format` (string, optional): Format to return the content in (markdown or json)

- **obsidian_create_note**
  - Description: Create a new note or update an existing note in your Obsidian vault
  - Parameters:
    - `path` (string, required): Path to the note (relative to vault root)
    - `content` (string, required): Content to write to the note

- **obsidian_append_note**
  - Description: Append content to an existing note in your Obsidian vault
  - Parameters:
    - `path` (string, required): Path to the note (relative to vault root)
    - `content` (string, required): Content to append to the note

- **obsidian_patch_note**
  - Description: Insert or modify content at a specific location in a note
  - Parameters:
    - `path` (string, required): Path to the note (relative to vault root)
    - `operation` (string, optional): Operation to perform (append, prepend, replace)
    - `target_type` (string, optional): Type of target (heading, block, frontmatter)
    - `target` (string, required): Target identifier
    - `content` (string, required): Content to insert
    - `create_target_if_missing` (boolean, optional): Whether to create the target if it doesn't exist

- **obsidian_delete_note**
  - Description: Delete a note from your Obsidian vault
  - Parameters:
    - `path` (string, required): Path to the note (relative to vault root)
    - `confirm` (boolean, required): Confirmation to delete the note (must be true)
