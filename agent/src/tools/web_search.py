"""Web search tool for the agent."""

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..core.agent import CodingAgent


def register_web_tools(agent: "CodingAgent") -> None:
    """Register web search tools on the agent's tool registry."""

    agent.tools.register(
        name="web_search",
        description="Search the web using DuckDuckGo (no API key needed)",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"}
            },
            "required": ["query"],
        },
        handler=_duckduckgo_search,
    )


def _duckduckgo_search(query: str) -> str:
    """Search using DuckDuckGo HTML interface."""
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import quote
        import re

        url = f"https://html.duckduckgo.com/html/?q={quote(query)}"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

        with urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="replace")

        # Extract result snippets
        results = re.findall(
            r'class="result__snippet"[^>]*>(.*?)</a>', html, re.DOTALL
        )
        if not results:
            # Fallback: extract result URLs and titles
            results = re.findall(
                r'class="result__a"[^>]*>(.*?)</a>', html, re.DOTALL
            )

        clean = [re.sub(r"<[^>]+>", "", r).strip() for r in results[:5]]

        if not clean:
            return "No results found"

        return "\n\n".join(f"{i + 1}. {r}" for i, r in enumerate(clean))

    except Exception as e:
        return json.dumps({"error": str(e)})
