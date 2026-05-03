"""CLI interface with 80s-90s hacking aesthetic."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from src.config import Config
from src.core.agent import CodingAgent

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs

    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

VERSION = "0.1.0"

BANNER = r"""
 _______  _______  _______  _______  _______  _______
(  ____ \(  ____ \(  ___  )(       )(  ____ )(  ____ \
| (    \/| (    \/| (   ) || () () || (    )|| (    \/
| |      | (__    | |   | || || || || (____)|| |
| |      |  __)   | |   | || |(_)| ||     __)| | ____
| |      | (      | |   | || |   | || (\ (   | | \_  )
| (____/\| (____/\| (___) || )   ( || ) \ \__| (___) |
(_______/(_______/(_______)|/     \||/   \__/(_______)

                  autonomous agent v{version}
""".format(version=VERSION)

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"
UNDERLINE = "\033[4m"


def print_banner() -> None:
    print(f"{CYAN}{BANNER}{RESET}")


def print_step(step: int, total: int, text: str) -> None:
    print(f"{YELLOW}{BOLD}>> Step {step}/{total}: {text}{RESET}")


def print_prompt(text: str) -> None:
    print(f"{CYAN}{BOLD}[?]{RESET} {text}")


def print_ok(text: str) -> None:
    print(f"{GREEN}[+]{RESET} {text}")


def print_error(text: str) -> None:
    print(f"{RED}[-]{RESET} {text}")


def print_info(text: str) -> None:
    print(f"{DIM}{text}{RESET}")


def print_fury(text: str) -> None:
    print(f"{MAGENTA}{BOLD}Fury >>{RESET} {text}")


def print_user(text: str) -> None:
    print(f"{GREEN}{BOLD}You >>{RESET} {text}")


def print_exec(text: str) -> None:
    print(f"{DIM}Executing: {text}{RESET}")


def print_success(text: str) -> None:
    print(f"{GREEN}[+]{RESET} {text}")


def input_styled(prompt_text: str, default: str = "") -> str:
    if default:
        full = f"{prompt_text} [{default}]: "
    else:
        full = f"{prompt_text}: "

    try:
        result = input(f"{CYAN}{BOLD}[?]{RESET} {full}")
    except (EOFError, KeyboardInterrupt):
        print()
        sys.exit(0)

    return result.strip() or default


def progress_bar(label: str, duration: float, width: int = 20) -> None:
    filled = int(width * min(duration / 3.0, 1.0))
    bar = "\u2588" * filled + "\u2591" * (width - filled)
    print(f"{DIM}{label} [{bar}] {duration:.1f}s{RESET}")


class OnboardingWizard:
    """Interactive setup wizard."""

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path

    def run(self) -> Config:
        print_banner()
        print(f"{GREEN}Welcome to FuryAI. First time? Let's set things up.{RESET}")
        print()

        api_key = self._step_api_key()
        model = self._step_model()
        level = self._step_fury_level()
        workspace = self._step_workspace()

        self._save_config(api_key, model, level, workspace)

        print()
        print_ok(f"Configuration saved to {self.config_path}")
        print_ok(f"Workspace created at {workspace}")
        print()
        print_info("FuryAI is ready. Try:")
        print_info("  fury run \"Optimize my React app\"")
        print_info("  fury chat  # Interactive mode")
        print_info("  fury status # Show agent state")
        print()

        return Config(
            api_key=api_key,
            workspace=Path(workspace),
            model=model,
            max_iterations=int(level),
        )

    def _step_api_key(self) -> str:
        print_step(1, 4, "API Key")
        print_info("Get your key at: https://openrouter.ai/keys")
        print()

        key = input_styled("OpenRouter API Key")
        if not key:
            print_error("API key is required")
            return self._step_api_key()

        print()
        return key

    def _step_model(self) -> str:
        print_step(2, 4, "Default Model")
        print()
        print(f"  {GREEN}1{RESET}) OpenAI GPT-oss-20b (free)")
        print(f"  {GREEN}2{RESET}) Nvidia Nemotron 120b (free)")
        print(f"  {GREEN}3{RESET}) Custom model ID")
        print()

        choice = input_styled("Choice", "1")

        models = {
            "1": "openai/gpt-oss-20b:free",
            "2": "nvidia/nemotron-3-super-120b-a12b:free",
        }

        model = models.get(choice)
        if not model:
            model = choice

        print()
        return model

    def _step_fury_level(self) -> str:
        print_step(3, 4, "Fury Level")
        print()
        print(f"  {GREEN}1{RESET} - Ask before every action (safe)")
        print(f"  {GREEN}5{RESET} - Plan then execute (recommended)")
        print(f"  {GREEN}10{RESET} - Full autonomy (for experts)")
        print()

        level = input_styled("Level", "5")

        try:
            level_int = int(level)
            if level_int < 1 or level_int > 10:
                raise ValueError
        except ValueError:
            print_error("Level must be 1-10")
            return self._step_fury_level()

        print()
        return level

    def _step_workspace(self) -> str:
        print_step(4, 4, "Workspace")
        print_info("Where should FuryAI work?")
        print()

        workspace = input_styled("Path", "./fury-workspace")
        print()
        return workspace

    def _save_config(
        self, api_key: str, model: str, level: str, workspace: str
    ) -> None:
        env_path = self.config_path
        env_path.write_text(
            f"OPENROUTER_API_KEY={api_key}\n"
            f"FURY_MODEL={model}\n"
            f"FURY_LEVEL={level}\n"
            f"FURY_WORKSPACE={workspace}\n"
        )


class ChatInterface:
    """Interactive chat with styled output."""

    def __init__(self, agent: CodingAgent, max_iterations: int = 5) -> None:
        self.agent = agent
        self.max_iterations = max_iterations
        self.session_tokens = 0
        self.skills: list[str] = []

    def run(self) -> None:
        print_banner()

        model_display = self.agent.llm.model.split("/")[-1]
        ws = self.agent.workspace.name

        print(f"{CYAN}{BOLD}[=] FuryAI v{VERSION} | model: {model_display} | level: {self.max_iterations}/10 [=]{RESET}")
        print(f"{CYAN}{BOLD}[=] workspace: {ws} | skills: {len(self.skills)} [=]{RESET}")
        print(f"{CYAN}{BOLD}[=] Type /help for commands, /exit to quit [=]{RESET}")
        print()

        self._load_skills()

        while True:
            try:
                user_input = input(f"{GREEN}{BOLD}You >>{RESET} ")
            except (EOFError, KeyboardInterrupt):
                print()
                self._save_skills()
                print_info("Session saved. See you later.")
                break

            if not user_input.strip():
                continue

            if user_input.startswith("/"):
                self._handle_command(user_input.strip())
                continue

            self._process_task(user_input.strip())

    def _handle_command(self, cmd: str) -> None:
        parts = cmd.split()
        command = parts[0].lower()

        if command == "/exit" or command == "/quit":
            self._save_skills()
            print_info("Session saved. See you later.")
            sys.exit(0)

        elif command == "/help":
            self._show_help()

        elif command == "/memory":
            self._show_memory()

        elif command == "/skills":
            self._show_skills()

        elif command == "/status":
            self._show_status()

        elif command == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
            print_banner()

        else:
            print_error(f"Unknown command: {command}")
            print_info("Type /help for available commands")

    def _show_help(self) -> None:
        print()
        print(f"{BOLD}Available commands:{RESET}")
        print(f"  {GREEN}/help{RESET}     - Show this help")
        print(f"  {GREEN}/memory{RESET}    - Show agent memory")
        print(f"  {GREEN}/skills{RESET}    - Show learned skills")
        print(f"  {GREEN}/status{RESET}    - Show agent status")
        print(f"  {GREEN}/clear{RESET}     - Clear screen")
        print(f"  {GREEN}/exit{RESET}      - Quit FuryAI")
        print()

    def _show_memory(self) -> None:
        memory_file = self.agent.workspace / "MEMORY.md"
        user_file = self.agent.workspace / "USER.md"

        memory = memory_file.read_text() if memory_file.exists() else "(empty)"
        user = user_file.read_text() if user_file.exists() else "(empty)"

        print()
        border = "-" * 55
        top = "+" + "-" * 55 + "+"
        bottom = "+" + "-" * 55 + "+"

        print(f"{CYAN}{top}{RESET}")
        print(f"{CYAN}|{RESET}{BOLD} FuryAI Memory {RESET}{' ' * 39}{CYAN}|{RESET}")
        print(f"{CYAN}{border}{RESET}")

        lines = user.strip().split("\n")[:5]
        for line in lines:
            cleaned = line.replace("#", "").replace("*", "").strip()
            if cleaned:
                print(f"{CYAN}|{RESET} User: {cleaned[:48]}")

        print(f"{CYAN}{border}{RESET}")

        lines = memory.strip().split("\n")[:5]
        for line in lines:
            cleaned = line.replace("#", "").replace("*", "").strip()
            if cleaned:
                print(f"{CYAN}|{RESET} {cleaned[:48]}")

        print(f"{CYAN}{border}{RESET}")
        print(f"{CYAN}|{RESET} Tokens used this session: {self.session_tokens}")
        print(f"{CYAN}{bottom}{RESET}")
        print()

    def _show_skills(self) -> None:
        if not self.skills:
            print_info("No skills learned yet.")
            return

        print()
        print(f"{BOLD}Learned skills:{RESET}")
        for skill in self.skills:
            print(f"  {GREEN}>{RESET} {skill}")
        print()

    def _show_status(self) -> None:
        ws = self.agent.workspace
        files = list(ws.glob("*"))
        ws_files = [f.name for f in files if f.name not in ("sandbox", "MEMORY.md", "USER.md")]

        print()
        print(f"{BOLD}Agent Status:{RESET}")
        print(f"  Model:     {self.agent.llm.model}")
        print(f"  Workspace: {ws}")
        print(f"  Files:     {len(ws_files)}")
        for f in ws_files:
            print(f"    {GREEN}>{RESET} {f}")
        print(f"  Skills:    {len(self.skills)}")
        print()

    def _process_task(self, task: str) -> None:
        print()
        print_fury("Analyzing task...")
        start = time.time()

        try:
            result = self.agent.run(task, max_iterations=self.max_iterations)
            duration = time.time() - start

            progress_bar("Processing", duration)
            print()

            print_fury(result)
            print()

            if len(task) > 30:
                skill_name = task[:30].lower().replace(" ", "-")
                if skill_name not in self.skills:
                    self.skills.append(skill_name)
                    print_info(f"Skill saved: \"{skill_name}\"")

        except Exception as e:
            print_error(f"Error: {e}")
            print()

    def _load_skills(self) -> None:
        skills_file = self.agent.workspace / "SKILLS.json"
        if skills_file.exists():
            try:
                self.skills = json.loads(skills_file.read_text())
            except (json.JSONDecodeError, ValueError):
                self.skills = []

    def _save_skills(self) -> None:
        skills_file = self.agent.workspace / "SKILLS.json"
        skills_file.write_text(json.dumps(self.skills, indent=2))


def run_onboarding() -> Config:
    """Run the setup wizard."""
    wizard = OnboardingWizard(Path(".env"))
    return wizard.run()


def run_interactive(config: Config) -> None:
    """Start interactive chat session."""
    agent = CodingAgent(
        api_key=config.api_key,
        workspace=config.workspace,
        model=config.model,
    )
    chat = ChatInterface(agent, max_iterations=config.max_iterations)
    chat.run()


def run_task(config: Config, task: str) -> None:
    """Run a single task."""
    agent = CodingAgent(
        api_key=config.api_key,
        workspace=config.workspace,
        model=config.model,
    )

    print_banner()
    print_fury(f"Processing: {task}")
    print()

    start = time.time()
    result = agent.run(task, max_iterations=config.max_iterations)
    duration = time.time() - start

    progress_bar("Processing", duration)
    print()
    print_fury(result)


def show_status(config: Config) -> None:
    """Show agent status."""
    ws = config.workspace
    print(f"{BOLD}FuryAI Status:{RESET}")
    print(f"  Model:     {config.model}")
    print(f"  Workspace: {ws}")
    print(f"  Level:     {config.max_iterations}/10")

    if ws.exists():
        files = list(ws.glob("*"))
        print(f"  Files:     {len(files)}")
    else:
        print_info("  Workspace not yet created")

    print()


def list_models(config: Config) -> None:
    """List available OpenRouter models."""
    import requests

    print(f"{BOLD}Available free models on OpenRouter:{RESET}")
    print()

    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {config.api_key}"},
            timeout=15,
        )
        models = [m for m in resp.json()["data"] if ":free" in m["id"]]
        for m in sorted(models, key=lambda x: x["id"])[:30]:
            ctx = m.get("context_length", "?")
            print(f"  {GREEN}>{RESET} {m['id']} (ctx: {ctx})")
    except Exception as e:
        print_error(f"Failed to fetch models: {e}")

    print()


def cli() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description=f"FuryAI v{VERSION} - Autonomous Coding Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  run TASK     Execute a task
  chat         Start interactive chat
  setup        Run setup wizard
  config       Show current configuration
  status       Show agent status
  models       List available models
  feedback     Print feedback info

Examples:
  fury run "Create a Flask hello world app"
  fury chat
  fury setup
  fury status
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        choices=["run", "chat", "setup", "config", "status", "models", "feedback"],
        help="Command to execute",
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task description (for 'run' command)",
    )
    parser.add_argument(
        "--workspace", "-w",
        help="Override workspace directory",
    )
    parser.add_argument(
        "--model", "-m",
        help="Override model",
    )

    args = parser.parse_args()

    if args.command == "setup" or args.command is None:
        run_onboarding()
        return

    # Try loading config from .env
    env_path = Path(".env")
    if env_path.exists():
        from dotenv import load_dotenv

        load_dotenv()
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        model = os.environ.get("FURY_MODEL", "openai/gpt-oss-20b:free")
        level = int(os.environ.get("FURY_LEVEL", "5"))
        workspace = os.environ.get("FURY_WORKSPACE", "./fury-workspace")

        if not api_key:
            print_error("OPENROUTER_API_KEY not found in .env")
            print_info("Run 'fury setup' to configure")
            sys.exit(1)

        config = Config(
            api_key=api_key,
            workspace=Path(args.workspace or workspace),
            model=args.model or model,
            max_iterations=level,
        )
    else:
        print_info("No .env found. Running setup...")
        print()
        config = run_onboarding()

    if args.command == "run":
        if not args.task:
            print_error("Task is required for 'run' command")
            print_info("Usage: fury run \"your task here\"")
            sys.exit(1)
        run_task(config, args.task)

    elif args.command == "chat":
        run_interactive(config)

    elif args.command == "config":
        print(f"{BOLD}Current configuration:{RESET}")
        print(f"  Model:     {config.model}")
        print(f"  Workspace: {config.workspace}")
        print(f"  Level:     {config.max_iterations}/10")
        print(f"  API Key:   {config.api_key[:8]}...{config.api_key[-4:]}")
        print()

    elif args.command == "status":
        show_status(config)

    elif args.command == "models":
        list_models(config)

    elif args.command == "feedback":
        print(f"{BOLD}Feedback:{RESET}")
        print("  GitHub: https://github.com/your-username/fury-agent")
        print("  Issues: https://github.com/your-username/fury-agent/issues")
        print()
