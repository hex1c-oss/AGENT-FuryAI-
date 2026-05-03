# FuryAI

Autonomous coding agent with retro hacker aesthetic. MIT License.

```
 _______  _______  _______  _______  _______  _______
(  ____ \(  ____ \(  ___  )(       )(  ____ )(  ____ \
| (    \/| (    \/| (   ) || () () || (    )|| (    \/
| |      | (__    | |   | || || || || (____)|| |
| |      |  __)   | |   | || |(_)| ||     __)| | ____
| |      | (      | |   | || |   | || (\ (   | | \_  )
| (____/\| (____/\| (___) || )   ( || ) \ \__| (___) |
(_______/(_______/(_______)|/     \||/   \__/(_______)

                  autonomous agent v0.1.0
```

## Quick Start

```bash
# 1. Install
cd agent && pip install -e .

# 2. Setup (interactive wizard)
python -m src.main setup

# 3. Run a task
python -m src.main run "Create a Flask hello world app"
```

## Commands

```bash
# Execute a task
python -m src.main run "Write a Python script that sorts a list"

# Interactive chat
python -m src.main chat

# Setup wizard
python -m src.main setup

# Show configuration
python -m src.main config

# Show agent status
python -m src.main status

# List available free models
python -m src.main models

# Get help
python -m src.main --help
```

## Chat Commands

Inside `python -m src.main chat`:

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/memory` | Show agent memory |
| `/skills` | Show learned skills |
| `/status` | Show agent status |
| `/clear` | Clear screen |
| `/exit` | Quit FuryAI |

## Models

Default: `openai/gpt-oss-20b:free` (free, supports function calling)

Other free options:
- `nvidia/nemotron-3-super-120b-a12b:free`
- `qwen/qwen3-coder:free`
- `google/gemma-3-12b-it:free`

Override with `-m`:
```bash
python -m src.main run "Task" -m nvidia/nemotron-3-super-120b-a12b:free
```

## Architecture

- **LLM Provider** — OpenRouter API with fallback for models without native tool_choice support
- **Memory** — USER.md and MEMORY.md with hard length limits (2000/5000 chars)
- **Tool Registry** — Registry pattern for extensible tools
- **Sandbox** — Isolated command execution with timeout and output limits
- **Loop Detection** — Auto-detects repeated tool calls and terminates

## Development

```bash
pip install -e ".[dev]"
python -m pytest tests/ -v
python -m mypy src/ --strict
python -m ruff check src/ tests/
```
