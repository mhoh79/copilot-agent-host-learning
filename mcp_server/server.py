import json
import subprocess
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Prompt, PromptArgument


workspace_root = Path(__file__).resolve().parent.parent
mcp = FastMCP("workspace-tools")


# ─────────────────────────────────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────────────────────────────────

@mcp.tool()
def get_workspace_summary() -> str:
    """Return a short summary of the workspace root."""
    entries = sorted([p.name for p in workspace_root.iterdir() if not p.name.startswith(".")])
    return json.dumps(
        {
            "workspace_root": str(workspace_root),
            "entry_count": len(entries),
            "entries": entries,
        },
        indent=2,
    )


@mcp.tool()
def read_file_snippet(path: str, line_count: int = 5) -> str:
    """Return a short snippet from a workspace-relative file path."""
    target = (workspace_root / path).resolve()
    if not target.exists() or not target.is_file():
        return json.dumps({"error": "file not found"})
    try:
        target.relative_to(workspace_root)
    except ValueError:
        return json.dumps({"error": "path escapes workspace root"})

    lines = target.read_text(encoding="utf-8").splitlines()
    snippet = lines[: max(1, line_count)]
    return json.dumps({"path": path, "lines": snippet})


# ─────────────────────────────────────────────────────────────────────
# RESOURCES
# ─────────────────────────────────────────────────────────────────────

@mcp.resource("file://workspace-files")
def list_workspace_files() -> str:
    """List all Python files in the workspace."""
    py_files = sorted(workspace_root.glob("**/*.py"))
    files = [str(f.relative_to(workspace_root)) for f in py_files]
    return json.dumps({"python_files": files, "count": len(files)}, indent=2)


@mcp.resource("file://recent-commits")
def recent_commits() -> str:
    """Read git commit history (latest 5 commits)."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            commits = result.stdout.strip().split("\n")
            return json.dumps({"commits": commits, "count": len(commits)}, indent=2)
        else:
            return json.dumps({"error": "git command failed", "stderr": result.stderr})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.resource("file://test-results")
def test_results_summary() -> str:
    """Return a summary of pytest results (if available)."""
    test_dir = workspace_root / "tests"
    if not test_dir.exists():
        return json.dumps({"info": "No tests directory found"})
    
    test_files = list(test_dir.glob("test_*.py"))
    return json.dumps(
        {
            "test_directory": str(test_dir),
            "test_file_count": len(test_files),
            "test_files": [f.name for f in test_files],
            "info": "Run 'pytest' to execute tests",
        },
        indent=2,
    )


# ─────────────────────────────────────────────────────────────────────
# PROMPTS
# ─────────────────────────────────────────────────────────────────────

@mcp.prompt("analyze-code")
def prompt_analyze_code(file_path: str = "filestat.py") -> str:
    """Analyze code for bugs and improvements."""
    return f"""Please analyze the code in {file_path} for:
1. Potential bugs or edge cases
2. Code style and best practices
3. Performance issues
4. Security concerns
5. Suggestions for improvement

Consider the context of the workspace and provide specific, actionable feedback."""


@mcp.prompt("write-test")
def prompt_write_test(function_name: str = "scan_directory") -> str:
    """Template for writing pytest tests."""
    return f"""Write a comprehensive pytest test for the function '{function_name}'.

Include:
1. A docstring explaining what the test does
2. Test fixtures and setup as needed
3. At least 3 test cases covering normal, edge, and error scenarios
4. Clear assertion messages
5. Proper cleanup if needed

Follow the pytest conventions used in this workspace."""


@mcp.prompt("document-function")
def prompt_document_function(function_name: str = "scan_directory") -> str:
    """Template for generating docstrings."""
    return f"""Generate a comprehensive docstring for the function '{function_name}'.

The docstring should include:
1. A one-line summary of what the function does
2. A detailed description
3. Args section with types and descriptions
4. Returns section with type and description
5. Raises section if applicable
6. Example usage if relevant

Use the docstring style consistent with this codebase."""


if __name__ == "__main__":
    mcp.run(transport="stdio")

