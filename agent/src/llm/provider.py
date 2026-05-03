from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    role: str
    content: str | None
    tool_call_id: str | None = None
    name: str | None = None
    tool_calls: List[Dict[str, Any]] | None = None


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    @abstractmethod
    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """Send a chat request to the LLM.

        Returns:
            {
                "content": str | None,
                "tool_calls": list | None,
                "usage": {"input_tokens": int, "output_tokens": int}
            }
        """
