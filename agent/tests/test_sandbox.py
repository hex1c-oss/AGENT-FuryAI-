from pathlib import Path
import tempfile

from src.core.sandbox import Sandbox


def test_execute_command() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Sandbox(Path(tmp))
        result = sandbox.execute("echo hello")

        assert "hello" in result


def test_timeout() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Sandbox(Path(tmp))
        sandbox.TIMEOUT = 1

        # ping blocks for ~5 seconds on Windows (cmd.exe compatible)
        result = sandbox.execute("ping -n 6 127.0.0.1 > nul")
        assert "timed out" in result.lower()


def test_output_limit() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Sandbox(Path(tmp))
        sandbox.MAX_OUTPUT = 10

        result = sandbox.execute("echo 'A' * 1000")
        assert len(result) < 1000


def test_nonzero_exit_code() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Sandbox(Path(tmp))
        result = sandbox.execute("exit 42")
        assert "Exit code: 42" in result


def test_stderr_captured() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Sandbox(Path(tmp))
        result = sandbox.execute("echo error >&2")
        assert "STDERR:" in result
        assert "error" in result
