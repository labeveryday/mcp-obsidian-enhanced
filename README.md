# MCP Server for Obsidian

This project provides a Model Context Protocol (MCP) server for interacting with Obsidian vaults through AI assistants like Amazon Q.

## Overview

The Obsidian MCP server enables AI assistants to interact with your Obsidian vault without requiring the Obsidian application to be open. This integration allows for seamless knowledge management, note creation, organization, and search directly through AI assistants.

## Features

- File operations (read, create, update, delete)
- Active file management
- Folder management
- Search capabilities (text, advanced, semantic)
- Metadata handling
- Template support
- Knowledge management

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Obsidian with the Local REST API plugin installed and configured
- An API key for the Local REST API plugin

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/labeveryday/mcp-obsidian-enhanced.git
   cd mcp-obsidian-enhanced
   ```

2. Create a virtual environment and install the package:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .
   ```

3. Create a `.env` file with your Obsidian API key:
   ```bash
   cp .env.example .env
   # Edit .env and add your API key
   ```

## Usage

See [DOCUMENTATION.md](DOCUMENTATION.md) for detailed usage instructions, including:
- Running the server
- Testing with MCP Inspector
- Available tools and their parameters
- Configuration options

## Development

### Setting Up Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/labeveryday/mcp-obsidian-enhanced.git
   cd mcp-obsidian-enhanced
   ```

2. Create a virtual environment and install development dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

### Running Tests

```bash
pytest
```

## Contributing

Guidelines for contributing to the project will be provided here.

## License

License information will be provided here.
