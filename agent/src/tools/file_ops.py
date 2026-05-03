"""File operation tools for the agent."""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.agent import CodingAgent


def register_file_tools(agent: "CodingAgent") -> None:
    """Register file operation tools on the agent's tool registry."""

    agent.tools.register(
        name="list_files",
        description="List files in a directory",
        parameters={
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path relative to workspace (default: root)",
                }
            },
            "required": [],
        },
        handler=lambda path="": _list_files(agent.workspace, path),
    )

    agent.tools.register(
        name="delete_file",
        description="Delete a file",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path relative to workspace"}
            },
            "required": ["path"],
        },
        handler=lambda path: _delete_file(agent.workspace, path),
    )


def _list_files(workspace: Path, path: str = "") -> str:
    target = workspace / path if path else workspace
    if not target.is_dir():
        return f"Error: Not a directory: {path}"

    entries = []
    for entry in sorted(target.iterdir()):
        prefix = "D" if entry.is_dir() else "F"
        entries.append(f"{prefix} {entry.relative_to(workspace)}")

    return "\n".join(entries) if entries else "Directory is empty"


def _delete_file(workspace: Path, path: str) -> str:
    filepath = workspace / path
    if not filepath.exists():
        return f"Error: File not found: {path}"

    try:
        filepath.unlink()
        return f"Deleted: {path}"
    except Exception as e:
        return f"Error deleting file: {e}"
