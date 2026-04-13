from pathlib import Path
from typing import Any, Dict, List
from tools.base_tool import BaseTool


class FileTool(BaseTool):
    """
    Secure file operations tool.
    Restricts all operations within a base directory.
    """

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    def __init__(self, base_path: Path):
        super().__init__(
            name="file_tool",
            description="Handles safe file operations"
        )
        self.base_path = Path(base_path).resolve()

        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    # -----------------------------------
    # Internal Utilities
    # -----------------------------------

    def _resolve_path(self, file_path: str) -> Path:
        """
        Prevent path traversal attacks.
        """
        target_path = (self.base_path / file_path).resolve()

        if not str(target_path).startswith(str(self.base_path)):
            raise PermissionError("Path traversal detected")

        return target_path

    # -----------------------------------
    # Core Execution Router
    # -----------------------------------

    def _execute(self, input_data: Dict[str, Any], **kwargs) -> Any:
        action = input_data.get("action")

        if action == "read":
            return self.read(input_data.get("path"))

        elif action == "write":
            return self.write(
                input_data.get("path"),
                input_data.get("content", "")
            )

        elif action == "delete":
            return self.delete(input_data.get("path"))

        elif action == "exists":
            return self.exists(input_data.get("path"))

        elif action == "list":
            return self.list_dir(input_data.get("path", ""))

        else:
            raise ValueError(f"Unknown action: {action}")

    # -----------------------------------
    # File Operations
    # -----------------------------------

    def read(self, file_path: str) -> str:
        path = self._resolve_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} not found")

        if path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError("File too large")

        return path.read_text(encoding="utf-8")

    def write(self, file_path: str, content: str) -> str:
        path = self._resolve_path(file_path)

        if len(content.encode("utf-8")) > self.MAX_FILE_SIZE:
            raise ValueError("Content too large")

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return f"File written: {file_path}"

    def delete(self, file_path: str) -> str:
        path = self._resolve_path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"{file_path} not found")

        path.unlink()
        return f"File deleted: {file_path}"

    def exists(self, file_path: str) -> bool:
        path = self._resolve_path(file_path)
        return path.exists()

    def list_dir(self, dir_path: str = "") -> List[str]:
        path = self._resolve_path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"{dir_path} not found")

        if not path.is_dir():
            raise ValueError(f"{dir_path} is not a directory")

        return [p.name for p in path.iterdir()]