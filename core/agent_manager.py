from typing import Optional

from utils.logger import get_logger
from automation.task_executor import TaskExecutor

from agents.coding_agent import CodingAgent
from agents.automation_agent import AutomationAgent
from agents.research_agent import ResearchAgent
from agents.planner_agent import PlannerAgent


logger = get_logger("AgentManager")


class AgentManager:
    """
    🧠 Agent Manager

    Responsibilities:
    - Initialize all agents
    - Route tasks intelligently
    - Execute via TaskExecutor
    - Support planner (multi-step tasks)
    """

    def __init__(self, brain, memory=None, context=None):
        self.brain = brain
        self.executor = TaskExecutor()

        # Initialize agents
        self.coding = CodingAgent(brain, memory, context)
        self.automation = AutomationAgent()
        self.research = ResearchAgent(brain, memory, context)
        self.planner = PlannerAgent(brain, self, memory, context)

    # =============================
    # 🚀 MAIN ROUTER
    # =============================
    async def route(self, task: str) -> str:
        """
        Intelligent routing entry point
        """

        logger.info(f"[AgentManager] Routing task: {task}")

        intent = await self.detect_intent(task)

        if intent == "plan":
            return await self.execute_planner(task)

        elif intent == "code":
            return await self.execute_coding(task)

        elif intent == "research":
            return await self.execute_research(task)

        elif intent == "automation":
            return await self.execute_automation(task)

        else:
            return "I’m not sure how to handle that."

    # =============================
    # 🧠 INTENT DETECTION (LLM)
    # =============================
    async def detect_intent(self, task: str) -> str:
        prompt = f"""
Classify the user request into one of:
- plan (multi-step tasks)
- code (programming)
- research (information lookup)
- automation (system control)

Task:
{task}

Return only one word.
"""

        try:
            response = await self.brain.ask_async(prompt)
            return response.strip().lower()

        except Exception as e:
            logger.error(f"Intent detection failed: {e}")
            return "automation"

    # =============================
    # 🤖 EXECUTION METHODS
    # =============================
    async def execute_planner(self, task: str) -> str:
        logger.info("Using PlannerAgent")
        return await self.executor.execute_agent(self.planner, task)

    async def execute_coding(self, task: str) -> str:
        logger.info("Using CodingAgent")
        return await self.executor.execute_agent(self.coding, task)

    async def execute_research(self, task: str) -> str:
        logger.info("Using ResearchAgent")
        return await self.executor.execute_agent(self.research, task)

    async def execute_automation(self, task: str) -> str:
        logger.info("Using AutomationAgent")
        return await self.executor.execute(self.automation.run, task)

    # =============================
    # 🔀 DIRECT AGENT ACCESS (optional)
    # =============================
    async def run_agent(self, agent_name: str, task: str):
        agent_name = agent_name.lower()

        agent_map = {
            "coding": self.coding,
            "automation": self.automation,
            "research": self.research,
            "planner": self.planner,
        }

        agent = agent_map.get(agent_name)

        if not agent:
            return "Unknown agent."

        return await self.executor.execute_agent(agent, task)