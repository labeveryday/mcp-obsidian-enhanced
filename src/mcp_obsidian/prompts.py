"""MCP server prompts for Obsidian integration."""

from mcp.types import Prompt, PromptArgument

# Define available prompts
PROMPTS = {
    # Note Creation Template
    "create-note": Prompt(
        name="create-note",
        description="""Create a new note with a structured template.

IMPORTANT INSTRUCTIONS FOR LLM:
1. When a folder is specified but doesn't exist:
   - First create the folder by creating a placeholder note in that folder
   - Use obsidian_create_note with path 'folder/.folder' to create the folder
   - Then create the actual note in that folder

2. Required information gathering:
   - Always ask for the note title first (required)
   - Then ask for the folder location (optional, defaults to root)
   - Then ask for the template type (optional)
   - Finally ask for any tags (optional)

3. Note creation process:
   - First create the folder if needed
   - Then create the note with the provided information
   - Use the obsidian_create_note tool for both operations
   - Never use shell commands or direct file system operations""",
        arguments=[
            PromptArgument(
                name="title",
                description="Title of the note",
                required=True
            ),
            PromptArgument(
                name="folder",
                description="Folder path where to create the note (e.g., 'Projects/' or 'Daily Notes/')",
                required=False
            ),
            PromptArgument(
                name="template",
                description="Template to use (meeting, project, daily, or custom)",
                required=False
            ),
            PromptArgument(
                name="tags",
                description="Comma-separated list of tags to include",
                required=False
            )
        ]
    ),

    # Meeting Notes Template
    "meeting-notes": Prompt(
        name="meeting-notes",
        description="""Create a structured meeting notes template. 
        
IMPORTANT INSTRUCTIONS FOR LLM:
1. Available Tools:
   - obsidian_create_note: Creates a new note in the Obsidian vault
   - obsidian_list_files: Lists files in a folder
   - obsidian_read_note: Reads a note's content
   - obsidian_update_note: Updates an existing note
   - obsidian_append_note: Appends content to a note
   - obsidian_delete_note: Deletes a note
   - obsidian_search: Searches for notes
   - obsidian_get_active_file: Gets the currently active file

2. When a folder is specified but doesn't exist:
   - First create the folder by creating a placeholder note in that folder
   - Use obsidian_create_note with path 'folder/.folder' to create the folder
   - Then create the actual meeting note in that folder
   - NEVER use shell commands like mkdir or direct file system operations

3. Required information gathering:
   - Always ask for the meeting title first (required)
   - Then ask for the folder location (optional, defaults to 'Meetings/')
   - Then ask for the date (optional, defaults to today)
   - Finally ask for participants (optional)

4. Note creation process:
   - First create the folder if needed using obsidian_create_note
   - Then create the meeting note with the provided information
   - Use the obsidian_create_note tool for both operations
   - NEVER use shell commands or direct file system operations

5. Example tool usage:
   To create a folder:
   ```python
   await mcp.execute_tool("obsidian_create_note", {
       "path": "meetings-info/.folder",
       "content": "# Meetings Info\nThis folder contains meeting notes."
   })
   ```

   To create the meeting note:
   ```python
   await mcp.execute_tool("obsidian_create_note", {
       "path": "meetings-info/Test Meeting.md",
       "content": "# Test Meeting\n\nDate: 2024-05-18\n\n## Agenda\n- \n\n## Notes\n- \n\n## Action Items\n- [ ] \n\n## Next Steps\n- \n\n---\ntags: [meeting]"
   })
   ```

6. NEVER use these commands:
   - ❌ mkdir
   - ❌ ls
   - ❌ touch
   - ❌ Any other shell commands
   - ❌ Direct file system operations
   - ❌ fs_read
   - ❌ execute_bash

7. Tool Parameters:
   obsidian_create_note:
   - path: The path where to create the note (e.g., "meetings-info/Test Meeting.md")
   - content: The content of the note in markdown format

   obsidian_list_files:
   - folder: The folder to list files from (e.g., "meetings-info/")

   obsidian_read_note:
   - path: The path of the note to read

   obsidian_update_note:
   - path: The path of the note to update
   - content: The new content of the note

   obsidian_append_note:
   - path: The path of the note to append to
   - content: The content to append

   obsidian_delete_note:
   - path: The path of the note to delete

   obsidian_search:
   - query: The search query (can use operators like path:, tag:, file:, content:)

   obsidian_get_active_file:
   - No parameters needed""",
        arguments=[
            PromptArgument(
                name="title",
                description="Title of the meeting",
                required=True
            ),
            PromptArgument(
                name="date",
                description="Date of the meeting (YYYY-MM-DD)",
                required=False
            ),
            PromptArgument(
                name="participants",
                description="Comma-separated list of participants",
                required=False
            ),
            PromptArgument(
                name="folder",
                description="Folder to save the meeting notes in (will be created if it doesn't exist)",
                required=False
            )
        ]
    ),

    # Project Notes Template
    "project-notes": Prompt(
        name="project-notes",
        description="""Create a structured project notes template.

IMPORTANT INSTRUCTIONS FOR LLM:
1. When a folder is specified but doesn't exist:
   - First create the folder by creating a placeholder note in that folder
   - Use obsidian_create_note with path 'folder/.folder' to create the folder
   - Then create the actual project note in that folder

2. Required information gathering:
   - Always ask for the project title first (required)
   - Then ask for the folder location (optional, defaults to 'Projects/')
   - Then ask for the project status (optional)
   - Finally ask for the priority level (optional)

3. Note creation process:
   - First create the folder if needed
   - Then create the project note with the provided information
   - Use the obsidian_create_note tool for both operations
   - Never use shell commands or direct file system operations""",
        arguments=[
            PromptArgument(
                name="title",
                description="Project title",
                required=True
            ),
            PromptArgument(
                name="status",
                description="Project status (planning, in-progress, completed, on-hold)",
                required=False
            ),
            PromptArgument(
                name="priority",
                description="Project priority (high, medium, low)",
                required=False
            ),
            PromptArgument(
                name="folder",
                description="Folder to save the project notes in (will be created if it doesn't exist)",
                required=False
            )
        ]
    ),

    # Daily Notes Template
    "daily-notes": Prompt(
        name="daily-notes",
        description="""Create a daily note with predefined sections.

IMPORTANT INSTRUCTIONS FOR LLM:
1. When a folder is specified but doesn't exist:
   - First create the folder by creating a placeholder note in that folder
   - Use obsidian_create_note with path 'folder/.folder' to create the folder
   - Then create the actual daily note in that folder

2. Required information gathering:
   - Ask for the date first (optional, defaults to today)
   - Then ask for the folder location (optional, defaults to 'Daily Notes/')
   - Finally ask for any additional tags (optional)

3. Note creation process:
   - First create the folder if needed
   - Then create the daily note with the provided information
   - Use the obsidian_create_note tool for both operations
   - Never use shell commands or direct file system operations""",
        arguments=[
            PromptArgument(
                name="date",
                description="Date for the daily note (YYYY-MM-DD)",
                required=False
            ),
            PromptArgument(
                name="folder",
                description="Folder to save the daily note in (will be created if it doesn't exist)",
                required=False
            ),
            PromptArgument(
                name="tags",
                description="Additional tags to include",
                required=False
            )
        ]
    ),

    # Search and Compile Template
    "search-compile": Prompt(
        name="search-compile",
        description="""Search for notes and compile them into a single document.

IMPORTANT INSTRUCTIONS FOR LLM:
1. Search process:
   - Use obsidian_search tool to find matching notes
   - Validate that the search returned results
   - If no results, inform the user and suggest alternative search terms

2. Compilation process:
   - Read each matching note using obsidian_read_note
   - Format the content appropriately based on the requested format
   - Create a new note with the compiled content using obsidian_create_note

3. Output handling:
   - If output_path is specified, save the compilation there
   - If no output_path, return the compilation content
   - Ensure the output folder exists before saving""",
        arguments=[
            PromptArgument(
                name="query",
                description="Search query (can use operators like path:, tag:, file:, content:)",
                required=True
            ),
            PromptArgument(
                name="output_path",
                description="Path where to save the compiled note",
                required=False
            ),
            PromptArgument(
                name="format",
                description="Output format (summary, detailed, or raw)",
                required=False
            )
        ]
    ),

    # Note Summary Template
    "note-summary": Prompt(
        name="note-summary",
        description="""Generate a summary of a note's content.

IMPORTANT INSTRUCTIONS FOR LLM:
1. Note validation:
   - First check if the note exists using obsidian_read_note
   - If note doesn't exist, inform the user and suggest alternatives

2. Summary generation:
   - Read the note content using obsidian_read_note
   - Generate a summary based on the requested length
   - Include metadata if requested

3. Output handling:
   - Format the summary with clear sections
   - Include the original note path and date
   - Highlight key points and main topics""",
        arguments=[
            PromptArgument(
                name="path",
                description="Path to the note to summarize",
                required=True
            ),
            PromptArgument(
                name="length",
                description="Length of summary (short, medium, or long)",
                required=False
            ),
            PromptArgument(
                name="include_metadata",
                description="Whether to include note metadata in the summary",
                required=False
            )
        ]
    ),

    # Note Organization Template
    "organize-notes": Prompt(
        name="organize-notes",
        description="""Organize notes on a specific topic.

IMPORTANT INSTRUCTIONS FOR LLM:
1. Search process:
   - Use obsidian_search to find notes related to the topic
   - Validate that the search returned results
   - If no results, inform the user and suggest alternative topics

2. Organization process:
   - Analyze the found notes to suggest a structure
   - Consider the requested organization type (flat, hierarchical, or tags)
   - Create an index note explaining the organization

3. Implementation:
   - Create necessary folders using obsidian_create_note with .folder notes
   - Create an index note with the organization structure
   - Never use shell commands or direct file system operations""",
        arguments=[
            PromptArgument(
                name="topic",
                description="Topic to organize notes around",
                required=True
            ),
            PromptArgument(
                name="folder",
                description="Folder to organize within (will be created if it doesn't exist)",
                required=False
            ),
            PromptArgument(
                name="structure",
                description="Organization structure (flat, hierarchical, or tags)",
                required=False
            )
        ]
    )
}

def get_prompt(name: str) -> Prompt:
    """Get a prompt by name.
    
    Args:
        name: Name of the prompt to get
        
    Returns:
        The requested prompt
        
    Raises:
        ValueError: If the prompt doesn't exist
    """
    if name not in PROMPTS:
        raise ValueError(f"Unknown prompt: {name}")
    return PROMPTS[name]

def list_prompts() -> dict:
    """List all available prompts.
    
    Returns:
        Dictionary of prompt names and descriptions
    """
    return {name: prompt.description for name, prompt in PROMPTS.items()} 