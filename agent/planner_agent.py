import asyncio
from typing import List, Dict, Optional

from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("PlannerAgent")


class PlannerAgent(BaseAgent):
    """
    🧠 Planner Agent

    Capabilities:
    - Break tasks into steps
    - Assign steps to agents
    - Execute workflows
    - Handle retries & failures
    """

    def __init__(self, brain, agent_manager, memory=None, context=None):
        super().__init__("PlannerAgent", memory, context)
        self.brain = brain
        self.agent_manager = agent_manager

    # =============================
    # 🧠 MAIN EXECUTION
    # =============================
    async def run(self, task: str, metadata: Optional[Dict] = None) -> str:
        logger.info(f"[Planner] Planning task: {task}")

        # Step 1: Create plan
        plan = await self.create_plan(task)

        if not plan:
            return "Failed to create a plan."

        # Step 2: Execute plan
        results = await self.execute_plan(plan)

        return self.format_results(plan, results)

    # =============================
    # 🧠 PLAN GENERATION
    # =============================
    async def create_plan(self, task: str) -> List[Dict]:
        prompt = f"""
You are an AI task planner.

Break this task into clear actionable steps.

Task:
{task}

Return JSON list:
[
  {{
    "step": 1,
    "action": "...",
    "agent": "coding | automation | research"
  }}
]
"""

        try:
            response = await self.brain.ask_async(prompt)

            import json
            plan = json.loads(response)

            logger.info(f"Plan created: {plan}")
            return plan

        except Exception as e:
            logger.error(f"Plan generation failed: {e}")
            return []

    # =============================
    # ⚙️ PLAN EXECUTION
    # =============================
    async def execute_plan(self, plan: List[Dict]) -> List[str]:
        results = []

        for step in plan:
            action = step.get("action")
            agent_type = step.get("agent")

            logger.info(f"Executing step {step['step']} with {agent_type}")

            try:
                result = await self.execute_step(agent_type, action)
                results.append(result)

            except Exception as e:
                logger.error(f"Step failed: {e}")
                results.append("Step failed")

        return results

    # =============================
    # 🤖 AGENT ROUTING
    # =============================
    async def execute_step(self, agent_type: str, action: str) -> str:
        agent_type = agent_type.lower()

        if agent_type == "coding":
            return await self.agent_manager.coding.execute(action)

        elif agent_type == "automation":
            return await self.agent_manager.automation.execute(action)

        elif agent_type == "research":
            return await self.agent_manager.research.execute(action)

        else:
            return "Unknown agent type."

    # =============================
    # 📊 RESULT FORMAT
    # =============================
    def format_results(self, plan: List[Dict], results: List[str]) -> str:
        output = "\n🧠 EXECUTION PLAN:\n"

        for step, result in zip(plan, results):
            output += f"\nStep {step['step']}: {step['action']}"
            output += f"\nResult: {result}\n"

        return output