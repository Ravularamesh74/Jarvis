from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import traceback
import time


class ToolExecutionError(Exception):
    """Custom exception for tool failures"""
    pass


class BaseTool(ABC):
    """
    Abstract base class for all tools in JARVIS system.
    """

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

    # -----------------------------------
    # Core Execution Interface
    # -----------------------------------

    def execute(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Standard execution wrapper with error handling.
        """
        start_time = time.time()

        if not self._validate_input(input_data):
            raise ValueError(f"[{self.name}] Invalid input: {input_data}")

        try:
            result = self._execute(input_data, **kwargs)

            return self._format_response(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return self._format_response(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                traceback=traceback.format_exc()
            )

    async def aexecute(self, input_data: Any, **kwargs) -> Dict[str, Any]:
        """
        Async execution wrapper.
        """
        start_time = time.time()

        if not self._validate_input(input_data):
            raise ValueError(f"[{self.name}] Invalid input: {input_data}")

        try:
            result = await self._aexecute(input_data, **kwargs)

            return self._format_response(
                success=True,
                result=result,
                execution_time=time.time() - start_time
            )

        except Exception as e:
            return self._format_response(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                traceback=traceback.format_exc()
            )

    # -----------------------------------
    # Abstract Methods
    # -----------------------------------

    @abstractmethod
    def _execute(self, input_data: Any, **kwargs) -> Any:
        """
        Implement tool logic here (sync).
        """
        pass

    async def _aexecute(self, input_data: Any, **kwargs) -> Any:
        """
        Optional async override.
        Default falls back to sync execution.
        """
        return self._execute(input_data, **kwargs)

    # -----------------------------------
    # Validation & Formatting
    # -----------------------------------

    def _validate_input(self, input_data: Any) -> bool:
        """
        Override for custom validation.
        """
        return input_data is not None

    def _format_response(
        self,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        execution_time: Optional[float] = None,
        traceback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Standardized response format across all tools.
        """
        return {
            "tool": self.name,
            "success": success,
            "result": result,
            "error": error,
            "execution_time": execution_time,
            "traceback": traceback,
        }

    # -----------------------------------
    # Utility Methods
    # -----------------------------------

    def __repr__(self):
        return f"<Tool name={self.name}>"

    def info(self) -> Dict[str, str]:
        """
        Metadata for tool registry / LLM selection.
        """
        return {
            "name": self.name,
            "description": self.description
        }