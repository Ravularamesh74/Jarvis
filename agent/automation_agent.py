import asyncio
import os
import subprocess
import webbrowser
from typing import Dict, Any

from utils.logger import get_logger

logger = get_logger("AutomationAgent")


class AutomationAgent:
    def __init__(self):
        self.allowed_apps = {
            "chrome": "start chrome",
            "notepad": "notepad",
            "vscode": "code",
        }

    # =============================
    # 🚀 MAIN ENTRY
    # =============================
    async def run(self, task: str) -> str:
        task = task.lower()

        logger.info(f"[Automation] Task received: {task}")

        try:
            if "open" in task:
                return await self.handle_open(task)

            elif "search" in task:
                return await self.handle_search(task)

            elif "create file" in task:
                return await self.handle_file_create(task)

            elif "run command" in task:
                return await self.handle_shell(task)

            elif "system info" in task:
                return await self.system_info()

            return "I couldn't understand the automation request."

        except Exception as e:
            logger.error(f"Automation error: {e}")
            return "Automation failed due to an error."

    # =============================
    # 🖥️ OPEN APPLICATION
    # =============================
    async def handle_open(self, task: str) -> str:
        for app in self.allowed_apps:
            if app in task:
                command = self.allowed_apps[app]

                logger.info(f"Opening {app}")
                subprocess.Popen(command, shell=True)

                return f"Opening {app}"

        return "Application not allowed or not recognized."

    # =============================
    # 🌐 WEB SEARCH
    # =============================
    async def handle_search(self, task: str) -> str:
        query = task.replace("search", "").strip()

        if not query:
            return "What do you want me to search?"

        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)

        return f"Searching for {query}"

    # =============================
    # 📁 FILE CREATION
    # =============================
    async def handle_file_create(self, task: str) -> str:
        try:
            parts = task.split("create file")

            if len(parts) < 2:
                return "Please specify file name."

            filename = parts[1].strip()

            if not filename:
                return "Invalid file name."

            with open(filename, "w") as f:
                f.write("# Created by JARVIS\n")

            return f"File '{filename}' created successfully."

        except Exception as e:
            logger.error(e)
            return "File creation failed."

    # =============================
    # ⚙️ SHELL COMMAND EXECUTION
    # =============================
    async def handle_shell(self, task: str) -> str:
        command = task.replace("run command", "").strip()

        if not command:
            return "No command provided."

        # 🔐 SAFETY CHECK
        if self.is_dangerous(command):
            return "Command blocked for safety reasons."

        try:
            result = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=10
            )

            return result.decode("utf-8")

        except subprocess.CalledProcessError as e:
            return e.output.decode("utf-8")

        except Exception as e:
            logger.error(e)
            return "Command execution failed."

    # =============================
    # 🔐 SAFETY FILTER
    # =============================
    def is_dangerous(self, command: str) -> bool:
        blocked = ["rm -rf", "del /f", "shutdown", "format", "mkfs"]

        return any(bad in command for bad in blocked)

    # =============================
    # 💻 SYSTEM INFO
    # =============================
    async def system_info(self) -> str:
        try:
            import platform
            import psutil

            info = {
                "OS": platform.system(),
                "CPU": psutil.cpu_percent(interval=1),
                "RAM": psutil.virtual_memory().percent,
            }

            return str(info)

        except Exception as e:
            logger.error(e)
            return "Unable to fetch system info."

    # =============================
    # 🧠 SYSTEM CONTROL (used by orchestrator)
    # =============================
    def system_control(self, command: str) -> str:
        command = command.lower()

        if "shutdown" in command:
            return "Blocked for safety."

        if "volume up" in command:
            # extend with pycaw if needed
            return "Volume control not implemented."

        return "Unknown system command."