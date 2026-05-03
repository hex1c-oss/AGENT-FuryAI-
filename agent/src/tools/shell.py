"""Shell command tool for the agent."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.agent import CodingAgent


def register_shell_tools(agent: "CodingAgent") -> None:
    """Register shell tools on the agent's tool registry."""
    agent.tools.register(
        name="run_shell",
        description="Execute a shell command in the sandbox",
        parameters={
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to execute"}
            },
            "required": ["command"],
        },
        handler=agent.sandbox.execute,
    )
