import asyncio
import time
from typing import Callable, Any, Dict, Optional

from utils.logger import get_logger

logger = get_logger("TaskExecutor")


class TaskExecutor:
    """
    ⚙️ Task Execution Engine

    Features:
    - Async + sync execution
    - Retry mechanism
    - Timeout handling
    - Agent + tool execution
    """

    def __init__(self, max_retries: int = 2, timeout: int = 30):
        self.max_retries = max_retries
        self.timeout = timeout

    # =============================
    # 🚀 MAIN EXECUTION ENTRY
    # =============================
    async def execute(
        self,
        action: Callable,
        *args,
        metadata: Optional[Dict] = None,
        **kwargs
    ) -> Any:
        """
        Execute a function with retries + timeout
        """

        for attempt in range(self.max_retries + 1):
            try:
                logger.info(f"Executing task (attempt {attempt+1})")

                result = await self._run_with_timeout(action, *args, **kwargs)

                logger.info("Task completed successfully")
                return result

            except asyncio.TimeoutError:
                logger.warning("Task timeout exceeded")

            except Exception as e:
                logger.error(f"Execution error: {e}")

            if attempt < self.max_retries:
                await asyncio.sleep(1)  # backoff

        return "Task failed after retries."

    # =============================
    # ⏱️ TIMEOUT WRAPPER
    # =============================
    async def _run_with_timeout(self, action: Callable, *args, **kwargs):
        return await asyncio.wait_for(
            self._run(action, *args, **kwargs),
            timeout=self.timeout
        )

    # =============================
    # ⚙️ EXECUTION CORE
    # =============================
    async def _run(self, action: Callable, *args, **kwargs):
        if asyncio.iscoroutinefunction(action):
            return await action(*args, **kwargs)

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: action(*args, **kwargs))

    # =============================
    # 🤖 EXECUTE AGENT TASK
    # =============================
    async def execute_agent(self, agent, task: str):
        """
        Execute a task via agent
        """
        logger.info(f"Routing to agent: {agent.__class__.__name__}")
        return await self.execute(agent.execute, task)

    # =============================
    # 🔧 EXECUTE TOOL
    # =============================
    async def execute_tool(self, tool_func: Callable, *args, **kwargs):
        """
        Execute tool safely
        """
        return await self.execute(tool_func, *args, **kwargs)

    # =============================
    # 📊 BATCH EXECUTION
    # =============================
    async def execute_batch(self, tasks: list):
        """
        Run multiple tasks in parallel
        tasks = [(func, args, kwargs), ...]
        """
        coroutines = [
            self.execute(func, *args, **kwargs)
            for func, args, kwargs in tasks
        ]

        return await asyncio.gather(*coroutines, return_exceptions=True)