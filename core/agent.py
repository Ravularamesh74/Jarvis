import asyncio
from typing import Dict, Any, Optional

from utils.logger import get_logger
from automation.task_executor import TaskExecutor

logger = get_logger("CoreAgent")


class CoreAgent:
    """
    🧠 Core Agent Controller (Meta-Agent)

    Responsibilities:
    - Coordinate multiple agents
    - Decide execution strategy
    - Handle complex reasoning chains
    """

    def __init__(self, brain, agent_manager, memory=None, context=None):
        self.brain = brain
        self.agent_manager = agent_manager
        self.executor = TaskExecutor()
        self.memory = memory
        self.context = context

    # =============================
    # 🚀 MAIN ENTRY
    # =============================
    async def run(self, task: str) -> str:
        logger.info(f"[CoreAgent] Received task: {task}")

        # Step 1: Decide strategy
        strategy = await self.decide_strategy(task)

        # Step 2: Execute strategy
        if strategy["type"] == "single":
            return await self.execute_single(strategy["agent"], task)

        elif strategy["type"] == "multi":
            return await self.execute_multi(strategy["steps"])

        elif strategy["type"] == "direct":
            return await self.direct_llm(task)

        return "Unable to process request."

    # =============================
    # 🧠 STRATEGY DECISION
    # =============================
    async def decide_strategy(self, task: str) -> Dict[str, Any]:
        prompt = f"""
You are a meta AI system.

Task:
{task}

Decide execution strategy:

1. single → one agent handles it
2. multi → multiple steps with different agents
3. direct → just answer with LLM

Return JSON:

{{
  "type": "single | multi | direct",
  "agent": "coding | research | automation | planner",
  "steps": [
    {{"agent": "...", "task": "..."}}
  ]
}}
"""

        try:
            response = await self.brain.ask_async(prompt)

            import json
            return json.loads(response)

        except Exception as e:
            logger.error(f"Strategy decision failed: {e}")
            return {"type": "direct"}

    # =============================
    # 🤖 SINGLE AGENT EXECUTION
    # =============================
    async def execute_single(self, agent_name: str, task: str) -> str:
        logger.info(f"Executing single agent: {agent_name}")
        return await self.agent_manager.run_agent(agent_name, task)

    # =============================
    # 🔀 MULTI-AGENT EXECUTION
    # =============================
    async def execute_multi(self, steps: list) -> str:
        results = []

        for step in steps:
            agent = step.get("agent")
            subtask = step.get("task")

            logger.info(f"Step → {agent}: {subtask}")

            result = await self.agent_manager.run_agent(agent, subtask)
            results.append(f"{agent}: {result}")

        return "\n".join(results)

    # =============================
    # 🧠 DIRECT LLM RESPONSE
    # =============================
    async def direct_llm(self, task: str) -> str:
        return await self.brain.ask_async(task)