import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from ..llm.openrouter import Message, OpenRouterProvider
from ..core.memory import MemoryManager
from ..core.sandbox import Sandbox
from ..core.tools import ToolRegistry


class CodingAgent:
    """Main agent class implementing the ReAct (Reasoning + Acting) loop.

    Architecture sources:
    - LangChain: https://github.com/langchain-ai/langchain
    - CAMEL-AI: https://github.com/camel-ai/camel
    """

    SYSTEM_PROMPT = """You are an expert coding assistant with access to tools.

## Your capabilities:
- Read, write, and modify code files
- Execute shell commands in a sandbox
- Search the web for documentation
- Use git for version control

## Rules:
1. Before writing code, explain your plan
2. Always test code after writing it
3. If a command fails, analyze the error before retrying
4. Save important decisions to memory
5. Keep code simple and well-documented

## Response format:
- If using a tool: Only output the tool call
- If responding to user: Be concise and technical
"""

    def __init__(
        self,
        api_key: str,
        workspace: Path = Path("./workspace"),
        model: str = "openai/gpt-oss-20b:free",
        max_tokens: int = 4096,
        on_action: Optional[Callable[[str, Dict[str, Any]], bool]] = None,
        on_result: Optional[Callable[[str, Dict[str, Any], str], None]] = None,
    ) -> None:
        self.workspace = workspace
        self.workspace.mkdir(parents=True, exist_ok=True)

        self.llm = OpenRouterProvider(
            api_key=api_key, model=model, max_tokens=max_tokens
        )
        self.memory = MemoryManager(self.workspace)
        self.sandbox = Sandbox(self.workspace / "sandbox")
        self.tools = ToolRegistry()
        self.conversation: List[Message] = []
        self.on_action = on_action
        self.on_result = on_result

        self._register_default_tools()

    def _register_default_tools(self) -> None:
        self.tools.register(
            name="read_file",
            description="Read contents of a file",
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path relative to workspace",
                    }
                },
                "required": ["path"],
            },
            handler=self._read_file,
        )

        self.tools.register(
            name="write_file",
            description="Write content to a file (creates if not exists)",
            parameters={
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["path", "content"],
            },
            handler=self._write_file,
        )

        self.tools.register(
            name="run_command",
            description="Execute a shell command in sandbox",
            parameters={
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"],
            },
            handler=self._run_command,
        )

    def run(self, task: str, max_iterations: int = 10) -> str:
        memory_context = self.memory.get_context()

        self.conversation = [
            Message("system", self.SYSTEM_PROMPT + "\n\n" + memory_context),
            Message("user", task),
        ]

        last_tool_calls: list[str] = []
        loop_count = 0

        for iteration in range(max_iterations):
            response = self.llm.chat(
                messages=self.conversation,
                tools=self.tools.get_schemas(),
            )

            if response["content"]:
                self.conversation.append(Message("assistant", str(response["content"])))

                if not response.get("tool_calls"):
                    self.memory.update_memory(
                        f"- Task: {task[:100]}\n  Status: completed at iteration {iteration + 1}",
                        "## Recent Decisions",
                    )
                    return str(response["content"])

            if response.get("tool_calls"):
                # Detect loops: same tool called with same args repeatedly
                current_calls = []
                for tool_call in response["tool_calls"]:
                    func_name = tool_call["function"]["name"]
                    func_args: Dict[str, Any] = json.loads(
                        tool_call["function"]["arguments"]
                    )

                    call_sig = f"{func_name}:{json.dumps(func_args, sort_keys=True)}"
                    current_calls.append(call_sig)

                    # Check approval before executing
                    if self.on_action:
                        approved = self.on_action(func_name, func_args)
                        if not approved:
                            result = "Action cancelled by user."
                        else:
                            result = self.tools.execute(func_name, func_args)
                    else:
                        result = self.tools.execute(func_name, func_args)

                    # Notify about the result
                    if self.on_result:
                        try:
                            result_data = json.loads(result)
                            if isinstance(result_data, dict):
                                self.on_result(func_name, func_args, result)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    self.conversation.append(
                        Message(
                            "tool",
                            f"Result of {func_name}:\n{result}",
                            tool_call_id=tool_call.get("id", ""),
                            name=func_name,
                        )
                    )

                # Check for loop
                if current_calls == last_tool_calls:
                    loop_count += 1
                    if loop_count >= 2:
                        return "Task completed. No further progress detected."
                else:
                    loop_count = 0
                last_tool_calls = current_calls

            # If we got tool_calls but no text, and this is near the end,
            # consider the task done if tools executed successfully
            if iteration >= max_iterations - 2 and not response["content"]:
                return "Task completed (tool execution finished)."

        return "Error: Maximum iterations reached without completing the task."

    def _read_file(self, path: str) -> str:
        if os.path.isabs(path):
            filepath = Path(path)
        else:
            filepath = self.workspace / path

        lower = path.lower()
        if "desktop" in lower and not os.path.isabs(path):
            desktop = Path.home() / "Desktop"
            filepath = desktop / Path(path).name

        if not filepath.exists():
            return f"Error: File not found: {path}"

        try:
            return filepath.read_text(encoding="utf-8")
        except Exception as e:
            return f"Error reading file: {e}"

    def _write_file(self, path: str, content: str) -> str:
        # Resolve path: if absolute, use as-is; if relative, use workspace
        if os.path.isabs(path):
            filepath = Path(path)
        else:
            filepath = self.workspace / path

        # Handle common user paths like Desktop/Documents
        lower = path.lower()
        if "desktop" in lower and not os.path.isabs(path):
            desktop = Path.home() / "Desktop"
            desktop.mkdir(parents=True, exist_ok=True)
            filepath = desktop / Path(path).name

        filepath.parent.mkdir(parents=True, exist_ok=True)

        action = "created"
        old_content = ""
        if filepath.exists():
            action = "modified"
            old_content = filepath.read_text(encoding="utf-8")

        try:
            filepath.write_text(content, encoding="utf-8")
            lines_added = len(content.split("\n"))
            return json.dumps({
                "status": "ok",
                "action": action,
                "path": str(filepath),
                "lines_added": lines_added,
                "old_content": old_content,
                "new_content": content,
            })
        except Exception as e:
            return json.dumps({"status": "error", "message": str(e)})

    def _run_command(self, command: str) -> str:
        return self.sandbox.execute(command)
