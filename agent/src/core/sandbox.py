import os
import subprocess
from pathlib import Path


class Sandbox:
    """Isolated command execution environment.

    Safety:
    - Commands run in a dedicated directory
    - 60-second timeout
    - Output capped at 10,000 characters
    """

    TIMEOUT = 60
    MAX_OUTPUT = 10_000

    def __init__(self, sandbox_dir: Path) -> None:
        self.sandbox_dir = sandbox_dir.resolve()
        self.sandbox_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(self.sandbox_dir),
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT,
                env={
                    **os.environ,
                    "SANDBOX": "1",
                    "HOME": str(self.sandbox_dir),
                },
            )

            output: list[str] = []
            if result.stdout:
                output.append(result.stdout[: self.MAX_OUTPUT])
            if result.stderr:
                output.append(f"STDERR:\n{result.stderr[:self.MAX_OUTPUT]}")
            if result.returncode != 0:
                output.append(f"\nExit code: {result.returncode}")

            return "\n".join(output) if output else "Command executed with no output"

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {self.TIMEOUT} seconds"
        except Exception as e:
            return f"Error executing command: {e}"
