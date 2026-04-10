import asyncio
from typing import Dict, List, Any, Callable, Optional

from utils.logger import get_logger
from automation.task_executor import TaskExecutor

logger = get_logger("WorkflowEngine")


class WorkflowStep:
    def __init__(
        self,
        name: str,
        action: Callable,
        depends_on: Optional[List[str]] = None,
        condition: Optional[Callable] = None,
    ):
        self.name = name
        self.action = action
        self.depends_on = depends_on or []
        self.condition = condition


class WorkflowEngine:
    """
    ⚙️ Workflow Engine

    Features:
    - Step dependencies
    - Parallel execution
    - Conditional branching
    - Retry via TaskExecutor
    """

    def __init__(self):
        self.executor = TaskExecutor()

    # =============================
    # 🚀 EXECUTE WORKFLOW
    # =============================
    async def run(self, steps: List[WorkflowStep]) -> Dict[str, Any]:
        results = {}
        pending = {step.name: step for step in steps}

        logger.info("Starting workflow execution...")

        while pending:
            ready_steps = [
                step for step in pending.values()
                if all(dep in results for dep in step.depends_on)
            ]

            if not ready_steps:
                raise Exception("Circular dependency detected or no executable steps")

            # Execute ready steps in parallel
            tasks = [
                self.execute_step(step, results)
                for step in ready_steps
            ]

            step_results = await asyncio.gather(*tasks)

            for step, result in zip(ready_steps, step_results):
                results[step.name] = result
                del pending[step.name]

        logger.info("Workflow completed.")
        return results

    # =============================
    # ▶️ EXECUTE SINGLE STEP
    # =============================
    async def execute_step(self, step: WorkflowStep, results: Dict[str, Any]):
        logger.info(f"Executing step: {step.name}")

        # Check condition
        if step.condition:
            try:
                if not step.condition(results):
                    logger.info(f"Skipping step: {step.name} (condition false)")
                    return "Skipped"
            except Exception as e:
                logger.error(f"Condition failed: {e}")
                return "Condition error"

        try:
            result = await self.executor.execute(step.action, results)
            return result

        except Exception as e:
            logger.error(f"Step failed: {step.name} | {e}")
            return "Failed"