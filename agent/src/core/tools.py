import json
from typing import Any, Callable, Dict, List


class ToolRegistry:
    """Registry of agent tools.

    Pattern: Registry — allows adding tools without modifying core code.
    Source: Martin Fowler, Patterns of Enterprise Application Architecture
    """

    def __init__(self) -> None:
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable[..., str],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool '{name}' already registered")

        self._tools[name] = {
            "schema": {
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": parameters,
                },
            },
            "handler": handler,
        }

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool["schema"] for tool in self._tools.values()]

    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        if name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {name}"})

        try:
            handler = self._tools[name]["handler"]
            result = handler(**arguments)
            if isinstance(result, str):
                return result
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            return json.dumps(
                {"error": str(e), "tool": name, "arguments": arguments}
            )
