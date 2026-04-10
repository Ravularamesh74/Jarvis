import asyncio
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from utils.logger import get_logger

logger = get_logger("BaseAgent")


class BaseAgent(ABC):
    """
    🧠 Abstract Base Agent

    Provides:
    - Async execution lifecycle
    - Memory integration hooks
    - Context handling
    - Tool execution wrapper
    - Logging + tracing
    """

    def __init__(self, name: str, memory=None, context=None):
        self.name = name
        self.memory = memory
        self.context = context
        self.agent_id = str(uuid.uuid4())

    # =============================
    # 🚀 PUBLIC EXECUTION ENTRY
    # =============================
    async def execute(self, task: str, metadata: Optional[Dict] = None) -> str:
        """
        Full lifecycle execution:
        1. Pre-process
        2. Run core logic
        3. Post-process
        """

        logger.info(f"[{self.name}] Task: {task}")

        try:
            enriched_task = await self.pre_process(task, metadata)

            result = await self.run(enriched_task, metadata)

            final_output = await self.post_process(task, result)

            return final_output

        except Exception as e:
            logger.error(f"[{self.name}] Execution failed: {e}")
            return f"{self.name} failed to complete the task."

    # =============================
    # 🔄 PRE-PROCESSING
    # =============================
    async def pre_process(self, task: str, metadata: Optional[Dict]) -> str:
        """
        Inject memory/context before execution
        """

        if self.memory:
            memory_context = self.memory.retrieve(task)
        else:
            memory_context = None

        if self.context:
            task = self.context.enrich(task, memory_context)

        return task

    # =============================
    # 🧠 CORE LOGIC (ABSTRACT)
    # =============================
    @abstractmethod
    async def run(self, task: str, metadata: Optional[Dict]) -> str:
        """
        Must be implemented by child agents
        """
        pass

    # =============================
    # 🔄 POST-PROCESSING
    # =============================
    async def post_process(self, original_task: str, result: str) -> str:
        """
        Store memory + logging
        """

        if self.memory:
            self.memory.store(original_task, result)

        logger.info(f"[{self.name}] Result: {result}")

        return result

    # =============================
    # 🔧 TOOL EXECUTION WRAPPER
    # =============================
    async def execute_tool(self, tool_func, *args, **kwargs) -> Any:
        """
        Safe async wrapper for tools
        """

        try:
            if asyncio.iscoroutinefunction(tool_func):
                return await tool_func(*args, **kwargs)
            else:
                loop = asyncio.get_event_loop()
                return await loop.run_in_executor(None, lambda: tool_func(*args, **kwargs))

        except Exception as e:
            logger.error(f"[{self.name}] Tool execution failed: {e}")
            return None

    # =============================
    # 🔐 SAFETY CHECK
    # =============================
    def validate(self, task: str) -> bool:
        """
        Override for custom validation logic
        """
        return True

    # =============================
    # 🧠 CONTEXT UPDATE
    # =============================
    def update_context(self, key: str, value: Any):
        if self.context:
            self.context.set(key, value)

    # =============================
    # 📊 METADATA / TRACE
    # =============================
    def get_metadata(self) -> Dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.name,
        }