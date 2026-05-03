# ⚡ FuryAI

<p align="center">
  <pre>
 _______  _______  _______  _______  _______  _______
(  ____ \(  ____ \(  ___  )(       )(  ____ )(  ____ \
| (    \/| (    \/| (   ) || () () || (    )|| (    \/
| |      | (__    | |   | || || || || (____)|| |
| |      |  __)   | |   | || |(_)| ||     __)| | ____
| |      | (      | |   | || |   | || (\ (   | | \_  )
| (____/\| (____/\| (___) || )   ( || ) \ \__| (___) |
(_______/(_______/(_______)|/     \||/   \__/(_______)

                autonomous coding agent v0.1.0
  </pre>
</p>

<p align="center">
  <a href="https://github.com/anoshinilya21-debug/AGENT-FuryAI-/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python 3.10+">
  </a>
  <a href="https://openrouter.ai/">
    <img src="https://img.shields.io/badge/OpenRouter-200+-models-orange" alt="OpenRouter">
  </a>
  <a href="https://github.com/anoshinilya21-debug/AGENT-FuryAI-/actions">
    <img src="https://img.shields.io/badge/tests-18%20passing-brightgreen" alt="Tests">
  </a>
  <a href="https://github.com/astral-sh/ruff">
    <img src="https://img.shields.io/badge/style-ruff-EF4444" alt="Ruff">
  </a>
</p>

<p align="center">
  <strong>Open-source AI coding agent with a retro hacker soul.</strong><br>
  Zero dependencies on proprietary SDKs. One API key. Infinite possibilities.
</p>

---

FuryAI is an autonomous coding agent that thinks, acts, and learns. Built on the **ReAct** reasoning loop with a **Tool Registry** pattern, **persistent file-based memory**, and a **sandboxed execution environment**. It speaks OpenRouter — giving you access to **200+ models** from every major provider, with **free tier support** out of the box.

No vendor lock-in. No heavy frameworks. Just pure Python, clean architecture, and a terminal interface that looks like it crawled out of a 1995 hacker movie.

**Use any model** — OpenRouter (200+), OpenAI, Anthropic, Google, Nvidia, Qwen, Meta Llama, MiniMax, or any custom endpoint. Switch with a flag. No code changes.

## Features

| Feature | Details |
|---|---|
| **Real terminal UI** | Full CLI with onboarding wizard, interactive chat, slash commands, progress bars, and ASCII art |
| **Zero vendor lock-in** | OpenRouter API to 200+ models. Switch providers with `-m flag:free`. No SDK dependencies |
| **Persistent memory** | `USER.md` and `MEMORY.md` with hard length limits — forces the model to compress what matters |
| **Skill learning** | Auto-saves task patterns to `SKILLS.json`, loaded across sessions |
| **Loop detection** | Catches repeated tool-call cycles and terminates early |
| **Sandboxed execution** | Commands run in isolated directory with timeout (60s) and output limits (10k chars) |
| **Free tier ready** | Works with `openai/gpt-oss-20b:free` — no credit card needed |
| **MIT licensed** | Do whatever you want with it |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/anoshinilya21-debug/AGENT-FuryAI-.git
cd AGENT-FuryAI-/agent

# 2. Install
pip install -e .

# 3. Run (interactive setup wizard launches automatically)
python -m src.main
```

The first run launches a **4-step onboarding wizard**:

```
Welcome to FuryAI. First time? Let's set things up.

▸ Step 1/4: API Key
Get your key at: https://openrouter.ai/keys
[?] OpenRouter API Key: ••••••••••••••••••••••••••••••••

▸ Step 2/4: Default Model
  1) OpenAI GPT-oss-20b (free)
  2) Nvidia Nemotron 120b (free)
  3) Custom model ID
Choice [1]:

▸ Step 3/4: Fury Level
  1 - Ask before every action (safe)
  5 - Plan then execute (recommended)
  10 - Full autonomy (for experts)
Level [5]:

▸ Step 4/4: Workspace
Where should FuryAI work?
Path [./fury-workspace]:

✓ Configuration saved to .env
✓ Workspace created at ./fury-workspace
```

After setup, you're in. Every subsequent run reads your `.env` and skips the wizard.

## Getting Started

```bash
# Execute a task
python -m src.main run "Create a Flask hello world app"

# Interactive chat
python -m src.main chat

# Re-run setup wizard
python -m src.main setup

# Show current configuration
python -m src.main config

# Show agent status and workspace files
python -m src.main status

# List all available free models on OpenRouter
python -m src.main models

# Get help
python -m src.main --help
```

### Chat Commands

Inside `python -m src.main chat`:

| Command | Description |
|---|---|
| `/help` | Show available commands |
| `/memory` | Show agent memory in a styled box |
| `/skills` | Show learned skills from past sessions |
| `/status` | Show model, workspace, and file listing |
| `/clear` | Clear the terminal screen |
| `/exit` | Save and quit |

```
[=] FuryAI v0.1.0 | model: gpt-oss-20b:free | level: 5/10 [=]
[=] workspace: fury-workspace | skills: 0 [=]
[=] Type /help for commands, /exit to quit [=]

You >> Create a Python function that sorts a list using merge sort

Fury >> Analyzing task...
Processing [████████████████████] 42.3s

Fury >> I'll create a merge_sort.py file with the function.
✓ File created (merge_sort.py, 34 lines)
✓ Tests passed
Skill saved: "python-sorting-merge-sort"
```

### Free Models

FuryAI works with zero cost using OpenRouter's free tier. Best free models with function calling:

| Model | Context | Best For |
|---|---|---|
| `openai/gpt-oss-20b:free` | 128k | General coding, function calling |
| `nvidia/nemotron-3-super-120b-a12b:free` | 262k | Complex reasoning, large context |
| `qwen/qwen3-coder:free` | 262k | Code generation, specialized tasks |

Override the default model at any time:

```bash
python -m src.main run "Task" -m nvidia/nemotron-3-super-120b-a12b:free
```

See all 29 free models:

```bash
python -m src.main models
```

## Architecture

```
agent/
├── pyproject.toml          # Dependencies with pinned versions
├── README.md               # This file
├── .gitignore
├── src/
│   ├── main.py             # Entry point — delegates to CLI
│   ├── cli.py              # CLI interface, wizard, chat, commands
│   ├── config.py           # Configuration from .env + CLI args
│   ├── core/
│   │   ├── agent.py        # ReAct loop: think → act → observe
│   │   ├── memory.py       # USER.md / MEMORY.md management
│   │   ├── tools.py        # Tool registry (registry pattern)
│   │   └── sandbox.py      # Isolated command execution
│   ├── tools/
│   │   ├── file_ops.py     # Read, write, list, delete files
│   │   ├── shell.py        # Shell command execution
│   │   ├── git_ops.py      # Git status, commit, log
│   │   └── web_search.py   # DuckDuckGo web search (no API key)
│   └── llm/
│       ├── provider.py     # Abstract LLM provider interface
│       └── openrouter.py   # OpenRouter API implementation
├── tests/
│   ├── test_agent.py       # Agent loop, tool execution, mocking
│   ├── test_memory.py      # Memory limits, truncation, sections
│   └── test_sandbox.py     # Timeout, output limits, stderr
└── sandbox/                # Isolated directory for command execution
    └── .gitkeep
```

### Key Design Decisions

| Decision | Why | Source |
|---|---|---|
| **OpenRouter API** | Single endpoint for 200+ models, automatic routing, free tier | [OpenRouter docs](https://openrouter.ai/docs) |
| **ReAct loop** | Reasoning + Acting pattern proven in LangChain, CAMEL-AI | [LangChain](https://github.com/langchain-ai/langchain), [CAMEL-AI](https://github.com/camel-ai/camel) |
| **Tool Registry** | Add tools without modifying core code | [Martin Fowler, PoEAA](https://martinfowler.com/) |
| **File-based memory** | Hard length limits force the model to compress what matters | [Hermes Agent pattern](https://github.com/OpenRouterTeam/spawn) |
| **No heavy frameworks** | Only `requests` + `python-dotenv` — 2 runtime deps | KISS principle |
| **Loop detection** | Free models sometimes repeat tool calls; auto-terminate | Internal discovery |
| **Explicit UTF-8 encoding** | Windows defaults to cp1251, breaking non-ASCII content | Bugfix during development |

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -v

# Type checking (strict mode)
python -m mypy src/ --strict

# Linting
python -m ruff check src/ tests/

# Format code
python -m black src/ tests/
```

All checks must pass:
- **18 tests** covering agent loop, tools, memory, sandbox
- **mypy --strict** on 17 source files — zero errors
- **ruff** — all checks passed

### Runtime Dependencies

| Package | Version | Why |
|---|---|---|
| `requests` | 2.31.0 | HTTP client for OpenRouter API |
| `python-dotenv` | 1.0.1 | Load `.env` configuration |

### Dev Dependencies

| Package | Version | Why |
|---|---|---|
| `pytest` | 8.3.2 | Testing framework |
| `pytest-cov` | 5.0.0 | Coverage reporting |
| `mypy` | 1.11.1 | Static type checking |
| `types-requests` | 2.31.0.20240125 | Type stubs for requests |
| `black` | 24.8.0 | Code formatting |
| `ruff` | 0.6.2 | Fast linter |

## Configuration

All settings live in `.env` (created by the wizard):

```env
OPENROUTER_API_KEY=sk-or-v1-...
FURY_MODEL=openai/gpt-oss-20b:free
FURY_LEVEL=5
FURY_WORKSPACE=./fury-workspace
```

Override any setting from the CLI:

```bash
python -m src.main run "Task" -m anthropic/claude-3.5-sonnet -w ./my-project
```

## License

[MIT](LICENSE) — do whatever you want with it.

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/amazing-feature`
3. Make your changes
4. Run the checks: `pytest && mypy src/ --strict && ruff check src/ tests/`
5. Commit and push: `git commit -m "feat: amazing feature" && git push`
6. Open a Pull Request

### Code Style

- Follow existing conventions (typing, naming, imports)
- All code must pass `mypy --strict`
- All code must pass `ruff check`
- New features need tests

---

<p align="center">
  Built with ☕ and ANSI escape codes.
</p>
