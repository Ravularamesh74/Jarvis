import os
import platform
import subprocess
import asyncio
from typing import Optional

from utils.logger import get_logger

logger = get_logger("SystemControl")


class SystemControl:
    """
    ⚙️ System Control Layer

    Handles:
    - App launching
    - System commands
    - Volume / basic controls
    - Safe shell execution
    """

    def __init__(self):
        self.os_type = platform.system().lower()

        # Allowed apps (expand safely)
        self.allowed_apps = {
            "chrome": self._open_chrome,
            "notepad": self._open_notepad,
            "vscode": self._open_vscode,
        }

        # Blocked commands (critical safety)
        self.blocked_keywords = [
            "rm -rf",
            "format",
            "shutdown",
            "reboot",
            "mkfs",
            "del /f",
        ]

    # =============================
    # 🚀 PUBLIC API
    # =============================
    async def execute(self, command: str) -> str:
        command = command.lower().strip()

        logger.info(f"[SystemControl] Command: {command}")

        # Safety check
        if self.is_dangerous(command):
            return "❌ Command blocked for safety."

        # App control
        for app in self.allowed_apps:
            if app in command:
                return await self.allowed_apps[app]()

        # Volume control
        if "volume up" in command:
            return self.volume_up()

        if "volume down" in command:
            return self.volume_down()

        # Shell fallback
        return await self.run_shell(command)

    # =============================
    # 🔐 SAFETY CHECK
    # =============================
    def is_dangerous(self, command: str) -> bool:
        return any(bad in command for bad in self.blocked_keywords)

    # =============================
    # 🖥️ APP OPENERS
    # =============================
    async def _open_chrome(self) -> str:
        return await self._run_command("start chrome" if self.is_windows() else "google-chrome")

    async def _open_notepad(self) -> str:
        return await self._run_command("notepad" if self.is_windows() else "nano")

    async def _open_vscode(self) -> str:
        return await self._run_command("code")

    # =============================
    # 🔊 VOLUME CONTROL
    # =============================
    def volume_up(self) -> str:
        if self.is_windows():
            os.system("nircmd.exe changesysvolume 2000")
            return "🔊 Volume increased"
        return "Volume control not supported on this OS"

    def volume_down(self) -> str:
        if self.is_windows():
            os.system("nircmd.exe changesysvolume -2000")
            return "🔉 Volume decreased"
        return "Volume control not supported on this OS"

    # =============================
    # ⚙️ SAFE SHELL EXECUTION
    # =============================
    async def run_shell(self, command: str) -> str:
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if stderr:
                return stderr.decode()

            return stdout.decode()

        except Exception as e:
            logger.error(f"Shell execution failed: {e}")
            return "Command execution failed."

    async def _run_command(self, command: str) -> str:
        try:
            subprocess.Popen(command, shell=True)
            return f"✅ Executed: {command}"
        except Exception as e:
            logger.error(e)
            return "Failed to execute command."

    # =============================
    # 🧠 OS HELPERS
    # =============================
    def is_windows(self) -> bool:
        return self.os_type == "windows"

    def is_linux(self) -> bool:
        return self.os_type == "linux"

    def is_mac(self) -> bool:
        return self.os_type == "darwin"