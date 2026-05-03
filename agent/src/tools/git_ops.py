"""Git operations tool for the agent."""

import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.agent import CodingAgent


def register_git_tools(agent: "CodingAgent") -> None:
    """Register git tools on the agent's tool registry."""

    agent.tools.register(
        name="git_status",
        description="Show git status of the workspace",
        parameters={
            "type": "object",
            "properties": {},
            "required": [],
        },
        handler=lambda: _run_git(agent.workspace, "status"),
    )

    agent.tools.register(
        name="git_commit",
        description="Commit changes with a message",
        parameters={
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Commit message"}
            },
            "required": ["message"],
        },
        handler=lambda message: _run_git(agent.workspace, "commit", "-m", message),
    )

    agent.tools.register(
        name="git_log",
        description="Show recent git log entries",
        parameters={
            "type": "object",
            "properties": {
                "n": {
                    "type": "integer",
                    "description": "Number of entries (default: 5)",
                }
            },
            "required": [],
        },
        handler=lambda n=5: _run_git(agent.workspace, "log", "--oneline", f"-{n}"),
    )


def _run_git(workspace: Path, *args: str) -> str:
    cmd = ["git", "-C", str(workspace)] + list(args)
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return f"Git error: {result.stderr.strip()}"
        return result.stdout.strip() or "Command executed successfully"
    except subprocess.TimeoutExpired:
        return "Error: Git command timed out"
    except Exception as e:
        return f"Error: {e}"
