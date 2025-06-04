# Changelog

All notable changes to the Obsidian MCP Server Enhanced project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced error handling with more descriptive messages
- Improved documentation for all tools and prompts

## [0.1.2] - 2025-06-04

### Changed
- Moved non-functional tools to Phase 2 roadmap
- Updated README to reflect current working tools vs planned tools
- Reorganized project roadmap to clarify Phase 2 features

### Removed
- Removed `obsidian_search` tool implementation (moved to Phase 2)
- Removed `obsidian_summarize_note` tool implementation (moved to Phase 2)
- Removed `obsidian_search_and_compile` tool implementation (moved to Phase 2)
- Removed `obsidian_organize_notes` tool implementation (moved to Phase 2)
- Removed `organize-notes` prompt (moved to Phase 2)

## [0.1.1] - 2025-06-03

### Added
- Completed all Phase 1 core infrastructure components
- FastMCP integration for tools, resources, and prompts
- Configuration management with environment variables
- Async Obsidian API client for interacting with the Local REST API
- Basic file operations (read, create, update, append, delete)
- Basic folder operations (list files)
- Search functionality
- Daily notes creation
- Meeting notes creation
- Note summarization (placeholder implementation)
- Search and compile functionality (placeholder implementation)

### Changed
- Updated project status from "Phase 1 Partially Complete" to "Phase 1 Complete"
- Consolidated prompt implementation to use decorator-based approach exclusively
- Updated README to accurately reflect the current state of the project
- Improved error handling in the Obsidian API client

### Removed
- Removed unused prompts.py module
- Removed references to unimplemented features in documentation

## [0.1.0] - 2024-05-29

### Added
- Initial project structure
- Basic server implementation
- Configuration management
- Obsidian API client
- File operations tools
