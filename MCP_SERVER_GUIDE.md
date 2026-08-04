# Workspace Tools MCP Server

A local Model Context Protocol (MCP) server that integrates workspace data and AI-powered task templates with Copilot in VS Code.

## Features

### Tools (imperative actions)
- **`get_workspace_summary`** — Returns a quick overview of workspace structure (root path, entry count, files/folders)
- **`read_file_snippet`** — Reads a snippet from any workspace-relative file (up to N lines)

### Resources (static/dynamic data)
- **`file://workspace-files`** — Lists all Python files in the workspace (recursive)
- **`file://recent-commits`** — Reads the latest 5 git commits (if repo has commit history)
- **`file://test-results`** — Summarizes the test directory structure and available test files

### Prompts (pre-configured templates)
- **`analyze-code`** — Template for analyzing code for bugs, style, performance, and security
- **`write-test`** — Template for writing comprehensive pytest test cases
- **`document-function`** — Template for generating function docstrings

## Setup

The server is configured in `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "workspace-tools": {
      "command": "python",
      "args": ["mcp_server/server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

When you open the workspace in VS Code, the server will:
1. Start automatically
2. Discover all tools, resources, and prompts
3. Show a trust dialog (trust to enable in Copilot)

## Usage in Copilot Chat

### Using Tools
Tools are invoked automatically by Copilot when helpful:
```
@copilot Tell me about this workspace
```
Copilot will call `get_workspace_summary` to gather context.

### Using Resources
Attach resources as context in Copilot chat:
1. Type `/` in the chat (or use the **+** icon)
2. Select **Add Context** → **MCP Resources**
3. Choose:
   - `workspace-files` — for file inventory
   - `recent-commits` — for git history context
   - `test-results` — for test coverage context

### Using Prompts
Invoke prompt templates by typing `/`:
```
/workspace-tools.analyze-code
```
You can also override default parameters:
```
/workspace-tools.write-test function_name=fetch_user_by_id
/workspace-tools.document-function function_name=calculate_total_cost
```

## Testing

Run the test client to verify the server:

```bash
python "C:\Users\matti\.copilot\session-state\95c28ca2-5a44-4be0-8fed-ed20baa18605\files\test_mcp_client.py"
```

This will:
- List all discoverable tools, resources, and prompts
- Test tool invocation (get_workspace_summary)
- Test resource reading (workspace-files)
- Test prompt retrieval (analyze-code with default params)

## Architecture

The server uses **FastMCP**, a lightweight Python framework for building MCP servers.

**File Structure:**
- `mcp_server/server.py` — Server implementation with tools, resources, and prompts
- `mcp_server/requirements.txt` — FastMCP dependency
- `.vscode/mcp.json` — VS Code workspace MCP configuration

**Workspace Root Resolution:**
The server resolves workspace paths relative to its own location:
```python
workspace_root = Path(__file__).resolve().parent.parent
```
This ensures all file operations stay within the workspace for security.

## Extending the Server

### Adding a Tool
```python
@mcp.tool()
def my_tool(param: str) -> str:
    """Description of what this tool does."""
    return json.dumps({"result": ...})
```

### Adding a Resource
```python
@mcp.resource("file://my-resource")
def my_resource() -> str:
    """Description of this resource."""
    return json.dumps({"data": ...})
```

### Adding a Prompt
```python
@mcp.prompt("my-prompt")
def prompt_my_prompt(file_name: str = "default.py") -> str:
    """Description of this prompt."""
    return f"""You are a helpful assistant.
    Analyze the file: {file_name}
    ..."""
```

## Security Notes

- **Workspace-scoped:** All file operations are confined to the workspace root
- **Read-only:** Resources and tools only read data (no mutations)
- **Trusted execution:** MCP server runs in the same process as VS Code Copilot
- **Path validation:** File paths are validated to prevent escaping the workspace

## Learning Resources

- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [FastMCP Documentation](https://modelcontextprotocol.io/quickstart)
- [VS Code Copilot MCP Integration](https://docs.github.com/en/copilot/about-copilot/copilot-features#copilot-in-vs-code)

## Troubleshooting

### Server not starting
- Check `.vscode/mcp.json` syntax
- Ensure `mcp_server/requirements.txt` is installed: `pip install -r mcp_server/requirements.txt`

### Tools not discoverable
- Reload VS Code window (Cmd/Ctrl+Shift+P → Developer: Reload Window)
- Check server logs in the MCP inspection pane

### Resource read fails
- Verify the resource URI includes `file://` prefix
- Ensure the workspace path is absolute and correct

### Prompts not showing
- Verify prompt name is used with `/workspace-tools.prompt-name` syntax
- Check that prompt decorator includes description
