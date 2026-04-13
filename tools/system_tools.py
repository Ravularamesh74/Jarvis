import os
import platform
import subprocess
import psutil
from typing import Any, Dict, List

from tools.base_tool import BaseTool


class SystemTool(BaseTool):
    """
    Secure system interaction tool.
    """

    # Whitelisted commands only
    ALLOWED_COMMANDS = [
        "echo",
        "ls",
        "dir",
        "pwd",
        "whoami"
    ]

    def __init__(self):
        super().__init__(
            name="system_tool",
            description="Handles safe system-level operations"
        )

    # -----------------------------------
    # Core Router
    # -----------------------------------

    def _execute(self, input_data: Dict[str, Any], **kwargs):
        action = input_data.get("action")

        if action == "run":
            return self.run_command(input_data.get("command"))

        elif action == "process_list":
            return self.list_processes()

        elif action == "kill":
            return self.kill_process(input_data.get("pid"))

        elif action == "system_info":
            return self.system_info()

        elif action == "env":
            return self.get_env(input_data.get("key"))

        else:
            raise ValueError(f"Unknown action: {action}")

    # -----------------------------------
    # Command Execution (SAFE)
    # -----------------------------------

    def run_command(self, command: str) -> Dict[str, Any]:
        if not command:
            raise ValueError("Command is required")

        cmd = command.split()[0]

        if cmd not in self.ALLOWED_COMMANDS:
            raise PermissionError(f"Command not allowed: {cmd}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )

            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"error": "Command timed out"}

    # -----------------------------------
    # Process Management
    # -----------------------------------

    def list_processes(self) -> List[Dict[str, Any]]:
        processes = []

        for proc in psutil.process_iter(attrs=["pid", "name", "cpu_percent"]):
            try:
                processes.append(proc.info)
            except Exception:
                continue

        return processes[:20]  # limit for safety

    def kill_process(self, pid: int) -> str:
        if not pid:
            raise ValueError("PID required")

        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return f"Process {pid} terminated"

        except psutil.NoSuchProcess:
            return f"Process {pid} not found"

        except Exception as e:
            return f"Error: {str(e)}"

    # -----------------------------------
    # System Information
    # -----------------------------------

    def system_info(self) -> Dict[str, Any]:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "cpu_count": psutil.cpu_count(),
            "memory": psutil.virtual_memory()._asdict(),
        }

    # -----------------------------------
    # Environment Variables (SAFE)
    # -----------------------------------

    SAFE_ENV_KEYS = [
        "PATH",
        "HOME",
        "USER",
        "USERNAME"
    ]

    def get_env(self, key: str) -> str:
        if key not in self.SAFE_ENV_KEYS:
            raise PermissionError(f"Access denied for env key: {key}")

        return os.environ.get(key, "")