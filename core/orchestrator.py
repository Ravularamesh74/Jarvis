from utils.logger import get_logger

from core.brain import Brain
from core.context_manager import ContextManager
from core.agent import CoreAgent

from agents.agent_manager import AgentManager
from memory.memory import Memory

logger = get_logger("Orchestrator")


class Orchestrator:
    """
    🧠 Central Orchestrator

    Flow:
    User Input
      ↓
    Context + Memory Enrichment
      ↓
    CoreAgent (decision)
      ↓
    AgentManager (execution)
      ↓
    Response
      ↓
    Memory + Context update
    """

    def __init__(self):
        # Core systems
        self.brain = Brain()
        self.context = ContextManager()
        self.memory = Memory()

        # Agent layer
        self.agent_manager = AgentManager(
            brain=self.brain,
            memory=self.memory,
            context=self.context
        )

        self.core_agent = CoreAgent(
            brain=self.brain,
            agent_manager=self.agent_manager,
            memory=self.memory,
            context=self.context
        )

    # =============================
    # 🚀 MAIN ENTRY
    # =============================
    async def handle(self, user_input: str) -> str:
        logger.info(f"[Orchestrator] Input: {user_input}")

        try:
            # Step 1: Retrieve memory
            memory_context = self.memory.retrieve(user_input)

            # Step 2: Enrich input with context
            enriched_input = self.context.enrich(user_input, memory_context)

            # Step 3: Run through CoreAgent
            response = await self.core_agent.run(enriched_input)

            # Step 4: Update memory + context
            self.context.add("user", user_input)
            self.context.add("assistant", response)

            self.memory.store(user_input, response)

            return response

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")

            # Fallback to direct LLM
            return await self.brain.ask_async(user_input)

    # =============================
    # ⚡ SIMPLE MODE (OPTIONAL)
    # =============================
    async def handle_simple(self, user_input: str) -> str:
        """
        Skip CoreAgent (faster, less intelligent)
        """
        return await self.agent_manager.route(user_input)

    # =============================
    # 🔄 RESET SYSTEM
    # =============================
    def reset(self):
        logger.info("Resetting system...")
        self.context.reset()
        self.memory.clear()

    # =============================
    # 📊 SYSTEM STATUS
    # =============================
    def status(self):
        return {
            "memory": self.memory.stats(),
            "context_length": len(self.context.get_history())
        }