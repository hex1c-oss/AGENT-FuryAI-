"""FuryAI - Autonomous Coding Agent v0.1.0."""

import sys

from src.cli import cli


def main() -> int:
    try:
        cli()
        return 0
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
