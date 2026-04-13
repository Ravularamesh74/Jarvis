import os
import time
import threading
import logging
import readline
from pathlib import Path
from typing import Generator, List, Dict, Any

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.table import Table
from rich.text import Text

# Optional voice
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_ENABLED = True
except ImportError:
    VOICE_ENABLED = False

# Core
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_store import VectorStore


# -----------------------------------
# CONFIG
# -----------------------------------

HISTORY_FILE = Path(".jarvis_history")
COMMANDS = ["/help", "/clear", "/exit", "/voice", "/sleep", "/agents", "/tools"]
WAKE_WORDS = ["jarvis", "hey jarvis"]


# -----------------------------------
# SYSTEM BUILD
# -----------------------------------

def build_system():
    short_term = ShortTermMemory(max_size=10)
    long_term = LongTermMemory(db=None)
    vector_store = VectorStore()

    memory = MemoryManager(short_term, long_term, vector_store)
    orchestrator = Orchestrator(memory=memory)

    # Optional: ensure these exist for dashboard
    if not hasattr(orchestrator, "tools_used"):
        orchestrator.tools_used: List[str] = []
    if not hasattr(orchestrator, "agents_state"):
        orchestrator.agents_state: Dict[str, str] = {
            "planner": "idle",
            "coding": "idle",
            "automation": "idle",
        }

    return orchestrator


# -----------------------------------
# AUTOCOMPLETE + HISTORY
# -----------------------------------

def completer(text, state):
    options = [cmd for cmd in COMMANDS if cmd.startswith(text)]
    return options[state] if state < len(options) else None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def load_history():
    if HISTORY_FILE.exists():
        readline.read_history_file(HISTORY_FILE)

def save_history():
    readline.write_history_file(HISTORY_FILE)


# -----------------------------------
# CLI
# -----------------------------------

class JarvisCLI:
    def __init__(self):
        self.console = Console()
        self.orchestrator = build_system()

        self.running = True
        self.voice_mode = False
        self.continuous_mode = False
        self.awake = False

        # buffers for dashboard
        self.last_response = ""
        self.recent_tools: List[str] = []
        self.last_user = ""

        load_history()

        # Voice setup
        if VOICE_ENABLED:
            self.recognizer = sr.Recognizer()
            self.tts = pyttsx3.init()
            self.mic = sr.Microphone()

    # -----------------------------------
    # DASHBOARD (RICH LIVE)
    # -----------------------------------

    def build_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="top", size=7),
            Layout(name="middle"),
            Layout(name="bottom", size=7),
        )

        # Top: status
        status_text = Text()
        status_text.append("JARVIS CLI ", style="bold green")
        status_text.append(f"| voice={self.voice_mode} ", style="cyan")
        status_text.append(f"| continuous={self.continuous_mode} ", style="cyan")
        status_text.append(f"| awake={self.awake}", style="yellow")

        layout["top"].update(Panel(status_text, title="Status"))

        # Middle: agents
        table = Table(expand=True)
        table.add_column("Agent")
        table.add_column("State")

        for k, v in self.orchestrator.agents_state.items():
            table.add_row(k, v)

        layout["middle"].update(Panel(table, title="Agents"))

        # Bottom: tools + last exchange
        tools = "\n".join(self.recent_tools[-5:]) or "No tools yet"
        convo = f"You: {self.last_user}\nJARVIS: {self.last_response[:200]}"

        bottom = Layout()
        bottom.split_row(
            Layout(Panel(tools, title="Tools"), ratio=1),
            Layout(Panel(convo, title="Recent"), ratio=2),
        )
        layout["bottom"].update(bottom)

        return layout

    # -----------------------------------
    # STREAMING OUTPUT
    # -----------------------------------

    def stream_output(self, gen: Generator[str, None, None]) -> str:
        self.console.print("[bold green]JARVIS:[/bold green] ", end="")
        full = ""
        for tok in gen:
            print(tok, end="", flush=True)
            full += tok
        print()
        return full

    # -----------------------------------
    # VOICE
    # -----------------------------------

    def listen_once(self, timeout=5, phrase_time_limit=8) -> str:
        if not VOICE_ENABLED:
            return ""
        with self.mic as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_time_limit
                )
            except Exception:
                return ""
        try:
            return self.recognizer.recognize_google(audio).lower()
        except Exception:
            return ""

    def speak(self, text: str):
        if VOICE_ENABLED:
            self.tts.say(text)
            self.tts.runAndWait()

    # -----------------------------------
    # WAKE WORD LOOP
    # -----------------------------------

    def wake_word_loop(self):
        """
        Background loop that waits for 'jarvis'
        """
        while self.running and self.continuous_mode:
            heard = self.listen_once(timeout=3, phrase_time_limit=3)
            if not heard:
                continue

            if any(w in heard for w in WAKE_WORDS):
                self.awake = True
                self.console.print("[yellow]Wake word detected[/yellow]")
                # listen for command immediately after wake
                cmd = self.listen_once(timeout=5, phrase_time_limit=10)
                if cmd:
                    self.process_input(cmd, via_voice=True)
                self.awake = False

    # -----------------------------------
    # TOOL LOGS
    # -----------------------------------

    def update_tools(self):
        tools = getattr(self.orchestrator, "tools_used", [])
        if tools:
            self.recent_tools.append(tools[-1])

    # -----------------------------------
    # COMMANDS
    # -----------------------------------

    def handle_command(self, cmd: str):
        if cmd == "/help":
            self.console.print("""
[bold yellow]Commands[/bold yellow]
/help    help
/clear   clear screen
/exit    exit
/voice   toggle voice
/sleep   toggle continuous wake-word mode
/agents  show agents panel once
/tools   show recent tools
            """)
        elif cmd == "/clear":
            os.system("cls" if os.name == "nt" else "clear")
        elif cmd == "/exit":
            self.running = False
        elif cmd == "/voice":
            self.voice_mode = not self.voice_mode
            self.console.print(f"[green]voice={self.voice_mode}[/green]")
        elif cmd == "/sleep":
            self.continuous_mode = not self.continuous_mode
            self.console.print(f"[green]continuous={self.continuous_mode}[/green]")
            if self.continuous_mode:
                t = threading.Thread(target=self.wake_word_loop, daemon=True)
                t.start()
        elif cmd == "/agents":
            self.console.print(self.build_layout())
        elif cmd == "/tools":
            tools = "\n".join(self.recent_tools[-10:]) or "No tools yet"
            self.console.print(Panel(tools, title="Tools"))
        else:
            self.console.print("[red]Unknown command[/red]")

    # -----------------------------------
    # PROCESS INPUT
    # -----------------------------------

    def process_input(self, user_input: str, via_voice=False):
        self.last_user = user_input

        # update agent states (example)
        self.orchestrator.agents_state["planner"] = "thinking"

        try:
            if hasattr(self.orchestrator, "stream"):
                gen = self.orchestrator.stream(user_input)
                response = self.stream_output(gen)
            else:
                response = self.orchestrator.handle(user_input)
                self.console.print(response)

            self.last_response = response

            # fake state transitions (you can wire real ones)
            self.orchestrator.agents_state["planner"] = "done"
            self.orchestrator.agents_state["coding"] = "idle"
            self.orchestrator.agents_state["automation"] = "idle"

            # update tools
            self.update_tools()

            if via_voice and self.voice_mode:
                self.speak(response[:200])

        except Exception as e:
            logging.error(str(e))
            self.console.print(f"[red]{str(e)}[/red]")

    # -----------------------------------
    # MAIN LOOP (WITH LIVE DASHBOARD)
    # -----------------------------------

    def run(self):
        self.console.print("[bold green]🤖 JARVIS CLI[/bold green]")

        with Live(self.build_layout(), refresh_per_second=4, console=self.console) as live:
            while self.running:
                try:
                    live.update(self.build_layout())

                    if self.continuous_mode:
                        # passive loop while wake-word thread runs
                        time.sleep(0.2)
                        continue

                    if self.voice_mode:
                        user_input = self.listen_once()
                        if not user_input:
                            continue
                        self.console.print(f"[cyan]You:[/cyan] {user_input}")
                    else:
                        user_input = input("\033[96mYou:\033[0m ").strip()

                    if not user_input:
                        continue

                    if user_input.startswith("/"):
                        self.handle_command(user_input)
                        continue

                    self.process_input(user_input, via_voice=self.voice_mode)

                except KeyboardInterrupt:
                    self.console.print("\n[red]Exiting...[/red]")
                    break

        save_history()


# -----------------------------------
# ENTRY
# -----------------------------------

if __name__ == "__main__":
    JarvisCLI().run()