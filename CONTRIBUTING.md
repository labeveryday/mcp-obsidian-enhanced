# Contributing to Obsidian MCP Server Enhanced

Thank you for considering contributing to the Obsidian MCP Server Enhanced project! This document provides guidelines and instructions for contributing.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/mcp-obsidian-enhanced.git
   cd mcp-obsidian-enhanced
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Create a `.env` file with your Obsidian API configuration:
   ```
   OBSIDIAN_API_KEY=your_api_key_from_local_rest_api_plugin
   OBSIDIAN_HOST=127.0.0.1
   OBSIDIAN_PORT=27124
   ```

## Development Workflow

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes, following the coding standards below
3. Add tests for your changes
4. Run the tests:
   ```bash
   pytest
   ```

5. Update documentation as needed
6. Commit your changes:
   ```bash
   git commit -m "Add your meaningful commit message here"
   ```

7. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

8. Create a pull request

## Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Document all functions, classes, and modules using docstrings
- Keep functions focused on a single responsibility
- Write tests for new functionality

## Adding New Tools

When adding new tools to the MCP server:

1. Add the tool function in `server.py` using the `@mcp.tool()` decorator
2. Provide comprehensive docstrings with examples
3. Implement proper error handling
4. Add tests for the new tool
5. Update the README to document the new tool

## Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update the CHANGELOG.md following the Keep a Changelog format
3. The PR should work on Python 3.10 and newer
4. The PR will be merged once it receives approval from a maintainer

## Code of Conduct

Please be respectful and inclusive in all interactions related to this project. We aim to foster an open and welcoming environment.

## Questions?

If you have any questions or need help, please open an issue on GitHub.
