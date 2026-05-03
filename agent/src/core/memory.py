from pathlib import Path


class MemoryManager:
    """Manages agent memory via USER.md and MEMORY.md files.

    Key idea: hard length limits force the model to compress information.
    Source: Pattern inspired by Hermes Agent
    - https://github.com/OpenRouterTeam/spawn
    """

    MAX_USER_MD_CHARS = 2000
    MAX_MEMORY_MD_CHARS = 5000

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.user_file = workspace / "USER.md"
        self.memory_file = workspace / "MEMORY.md"
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        if not self.user_file.exists():
            self.user_file.write_text(
                "# User Profile\n\n"
                "## Preferences\n"
                "- Language: \n"
                "- Code style: \n"
                "- Project: \n\n"
                "## Constraints\n"
                "- \n",
                encoding="utf-8",
            )

        if not self.memory_file.exists():
            self.memory_file.write_text(
                "# Agent Memory\n\n"
                "## Project Context\n\n"
                "## Recent Decisions\n\n"
                "## Lessons Learned\n",
                encoding="utf-8",
            )

    def get_context(self) -> str:
        user_content = self._read_file_with_limit(
            self.user_file, self.MAX_USER_MD_CHARS
        )
        memory_content = self._read_file_with_limit(
            self.memory_file, self.MAX_MEMORY_MD_CHARS
        )

        return (
            f"<user_profile>\n{user_content}\n</user_profile>\n\n"
            f"<agent_memory>\n{memory_content}\n</agent_memory>"
        )

    def update_memory(self, new_content: str, section: str = "## Recent Decisions") -> None:
        current = self.memory_file.read_text(encoding="utf-8")

        if section in current:
            parts = current.split(section)
            updated = f"{parts[0]}{section}\n{new_content}\n"

            if len(updated) > self.MAX_MEMORY_MD_CHARS:
                updated = self._truncate_old_entries(updated)

            self.memory_file.write_text(updated, encoding="utf-8")

    def _read_file_with_limit(self, filepath: Path, limit: int) -> str:
        content = filepath.read_text(encoding="utf-8")
        return content[:limit]

    def _truncate_old_entries(self, content: str) -> str:
        lines = content.split("\n")
        if len(lines) > 100:
            header = "\n".join(lines[:10])
            recent = "\n".join(lines[-80:])
            return f"{header}\n... (older entries truncated) ...\n{recent}"
        return content
