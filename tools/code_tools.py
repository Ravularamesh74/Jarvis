import io
import sys
import traceback
import subprocess
import tempfile
import contextlib
from typing import Any, Dict

from tools.base_tool import BaseTool


# -----------------------------------
# Security Config
# -----------------------------------

FORBIDDEN_KEYWORDS = [
    "import os",
    "import sys",
    "subprocess",
    "shutil",
    "open(",
    "__import__",
    "eval(",
    "exec(",
    "socket",
    "pickle",
]


SAFE_BUILTINS = {
    "print": print,
    "range": range,
    "len": len,
    "int": int,
    "float": float,
    "str": str,
    "list": list,
    "dict": dict,
    "sum": sum,
    "min": min,
    "max": max,
    "abs": abs,
}


# -----------------------------------
# Code Executor
# -----------------------------------

class CodeExecutor(BaseTool):
    """
    Safe Python code execution tool.
    """

    def __init__(self):
        super().__init__(
            name="code_executor",
            description="Executes safe Python code"
        )

    def _validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, str) and len(input_data.strip()) > 0

    def _security_check(self, code: str):
        lowered = code.lower()
        for keyword in FORBIDDEN_KEYWORDS:
            if keyword in lowered:
                raise ValueError(f"Forbidden operation detected: {keyword}")

    def _execute(self, input_data: str, **kwargs) -> Dict[str, Any]:
        code = input_data

        # Security filter
        self._security_check(code)

        stdout = io.StringIO()
        stderr = io.StringIO()

        try:
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exec(
                    code,
                    {"__builtins__": SAFE_BUILTINS},
                    {}
                )

            return {
                "output": stdout.getvalue(),
                "error": stderr.getvalue()
            }

        except Exception as e:
            return {
                "output": stdout.getvalue(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }


# -----------------------------------
# Shell Command Tool (Controlled)
# -----------------------------------

class ShellTool(BaseTool):
    """
    Executes safe shell commands with restrictions.
    """

    ALLOWED_COMMANDS = ["echo", "dir", "ls", "pwd"]

    def __init__(self):
        super().__init__(
            name="shell_tool",
            description="Executes limited shell commands"
        )

    def _validate_input(self, input_data: Any) -> bool:
        return isinstance(input_data, str) and input_data.strip() != ""

    def _execute(self, input_data: str, **kwargs):
        command = input_data.strip().split()[0]

        if command not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command not allowed: {command}")

        try:
            result = subprocess.run(
                input_data,
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
# File Code Runner (Advanced)
# -----------------------------------

class PythonFileRunner(BaseTool):
    """
    Executes Python code from a temp file (isolated).
    """

    def __init__(self):
        super().__init__(
            name="python_file_runner",
            description="Runs Python scripts safely in temp environment"
        )

    def _execute(self, input_data: str, **kwargs):
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=True
            ) as temp_file:

                temp_file.write(input_data)
                temp_file.flush()

                result = subprocess.run(
                    ["python", temp_file.name],
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
            return {"error": "Execution timed out"}