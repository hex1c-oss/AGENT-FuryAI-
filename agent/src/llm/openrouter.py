import time
from typing import Any, Dict, List, Optional

import requests

from .provider import LLMProvider, Message

__all__ = ["OpenRouterProvider", "Message"]


class OpenRouterProvider(LLMProvider):
    """OpenRouter API client.

    Sources:
    - API docs: https://openrouter.ai/docs/api-reference/overview
    - Models: https://openrouter.ai/models
    """

    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(
        self,
        api_key: str,
        model: str = "anthropic/claude-sonnet-4-20250514",
        max_tokens: int = 4096,
    ) -> None:
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required")

        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/coding-agent",
                "X-Title": "Coding Agent",
            }
        )

    def _format_message(self, msg: Message) -> Dict[str, Any]:
        formatted: Dict[str, Any] = {"role": msg.role, "content": msg.content}
        if msg.tool_call_id:
            formatted["tool_call_id"] = msg.tool_call_id
        if msg.name:
            formatted["name"] = msg.name
        if msg.tool_calls:
            formatted["tool_calls"] = msg.tool_calls
        return formatted

    def chat(
        self,
        messages: List[Message],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [self._format_message(m) for m in messages],
            "max_tokens": self.max_tokens,
            "temperature": temperature,
        }

        if tools:
            payload["tools"] = tools

        response = self.session.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
            timeout=300,
        )

        if response.status_code == 400 and tools:
            payload["tool_choice"] = "auto"
            response = self.session.post(
                f"{self.BASE_URL}/chat/completions",
                json=payload,
                timeout=300,
            )

        if response.status_code == 400:
            raise RuntimeError(
                f"OpenRouter API 400 error: {response.text[:300]}\n"
                f"Model '{self.model}' may not support function calling. "
                "Try a different model."
            )

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", "30"))
            time.sleep(retry_after)
            return self.chat(messages, tools, temperature)

        response.raise_for_status()

        data = response.json()
        choice = data["choices"][0]
        message = choice["message"]

        return {
            "content": message.get("content"),
            "tool_calls": message.get("tool_calls"),
            "usage": data.get("usage", {}),
        }
