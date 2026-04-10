import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Callable, Dict, Any, Optional, List

from utils.logger import get_logger

logger = get_logger("Scheduler")


class ScheduledTask:
    def __init__(
        self,
        name: str,
        action: Callable,
        run_at: Optional[datetime] = None,
        interval: Optional[int] = None,
        repeat: bool = False,
        metadata: Optional[Dict] = None,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.action = action
        self.run_at = run_at
        self.interval = interval  # seconds
        self.repeat = repeat
        self.metadata = metadata or {}
        self.next_run = run_at or datetime.utcnow()

    def should_run(self) -> bool:
        return datetime.utcnow() >= self.next_run

    def update_next_run(self):
        if self.repeat and self.interval:
            self.next_run = datetime.utcnow() + timedelta(seconds=self.interval)


class Scheduler:
    """
    ⏰ Async Task Scheduler

    Features:
    - One-time tasks
    - Recurring tasks (interval)
    - Async execution
    - Extendable persistence
    """

    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False

    # =============================
    # ➕ ADD TASK
    # =============================
    def add_task(
        self,
        name: str,
        action: Callable,
        delay: Optional[int] = None,
        interval: Optional[int] = None,
        repeat: bool = False,
        metadata: Optional[Dict] = None,
    ) -> str:
        run_at = None

        if delay:
            run_at = datetime.utcnow() + timedelta(seconds=delay)

        task = ScheduledTask(
            name=name,
            action=action,
            run_at=run_at,
            interval=interval,
            repeat=repeat,
            metadata=metadata,
        )

        self.tasks[task.id] = task
        logger.info(f"Task scheduled: {name} ({task.id})")

        return task.id

    # =============================
    # ❌ REMOVE TASK
    # =============================
    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f"Task removed: {task_id}")

    # =============================
    # 📋 LIST TASKS
    # =============================
    def list_tasks(self) -> List[Dict]:
        return [
            {
                "id": t.id,
                "name": t.name,
                "next_run": t.next_run,
                "repeat": t.repeat,
            }
            for t in self.tasks.values()
        ]

    # =============================
    # ▶️ EXECUTE TASK
    # =============================
    async def execute_task(self, task: ScheduledTask):
        logger.info(f"Executing task: {task.name}")

        try:
            if asyncio.iscoroutinefunction(task.action):
                await task.action(task.metadata)
            else:
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, lambda: task.action(task.metadata))

        except Exception as e:
            logger.error(f"Task failed: {task.name} | Error: {e}")

        finally:
            if task.repeat and task.interval:
                task.update_next_run()
            else:
                self.remove_task(task.id)

    # =============================
    # 🔄 MAIN LOOP
    # =============================
    async def run(self):
        self.running = True
        logger.info("Scheduler started...")

        while self.running:
            now = datetime.utcnow()

            for task in list(self.tasks.values()):
                if task.should_run():
                    asyncio.create_task(self.execute_task(task))

            await asyncio.sleep(1)

    # =============================
    # 🛑 STOP
    # =============================
    def stop(self):
        self.running = False
        logger.info("Scheduler stopped.")