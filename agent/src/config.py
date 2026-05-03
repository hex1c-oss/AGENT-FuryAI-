import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str
    workspace: Path = Path("./workspace")
    model: str = "openai/gpt-oss-20b:free"
    max_tokens: int = 4096
    fury_level: int = 5
    interactive: bool = False

    @property
    def max_iterations(self) -> int:
        if self.fury_level <= 3:
            return 15
        if self.fury_level <= 7:
            return 30
        return 50

    @classmethod
    def from_env_and_args(
        cls,
        workspace: str = "./workspace",
        model: str | None = None,
        max_iterations: int = 10,
        interactive: bool = False,
    ) -> "Config":
        load_dotenv()

        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            raise EnvironmentError(
                "OPENROUTER_API_KEY not set. "
                "Get a key at https://openrouter.ai/keys"
            )

        return cls(
            api_key=api_key,
            workspace=Path(workspace),
            model=model or "openai/gpt-oss-20b:free",
            fury_level=max_iterations,
            interactive=interactive,
        )
