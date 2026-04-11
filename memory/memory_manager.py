"""
JARVIS Memory Manager
--------------------
Acts as the central memory orchestrator.

Responsibilities:
- Route data between short-term and long-term memory
- Provide contextual memory to brain
- Handle memory prioritization
- Prepare for semantic/vector memory upgrade
"""

import logging
from typing import List, Optional

from memory.long_term import LongTermMemory

logger = logging.getLogger("JARVIS.Memory.Manager")
logger.setLevel(logging.INFO)


class MemoryManager:
    def __init__(self,
                 long_term: Optional[LongTermMemory] = None,
                 short_term_limit: int = 10):

        self.long_term = long_term or LongTermMemory()
        self.short_term_limit = short_term_limit

        # In-memory short-term cache
        self.short_term_buffer: List[dict] = []

    # =========================================================
    # STORE MESSAGE FLOW (CORE ENTRY)
    # =========================================================
    def store_interaction(self, user: str, message: str, response: str):
        """
        Store conversation in both short-term and long-term memory
        """

        interaction = {
            "user": user,
            "message": message,
            "response": response
        }

        # Short-term memory
        self.short_term_buffer.append(interaction)

        if len(self.short_term_buffer) > self.short_term_limit:
            self.short_term_buffer.pop(0)

        # Long-term memory
        self.long_term.store_conversation(user, message, response)

        logger.info(f"[MEMORY] Stored interaction for {user}")

    # =========================================================
    # CONTEXT BUILDER (VERY IMPORTANT)
    # =========================================================
    def build_context(self, query: str, user: str) -> str:
        """
        Build intelligent context for AI brain
        """

        context_parts = []

        # 1. Short-term memory (recent chat)
        for item in self.short_term_buffer[-5:]:
            context_parts.append(
                f"User: {item['message']}\nAI: {item['response']}"
            )

        # 2. Long-term semantic search (basic for now)
        related_memories = self.long_term.search(query)

        for mem in related_memories:
            context_parts.append(f"[Memory] {mem}")

        # 3. Knowledge recall (if exists)
        key_memory = self.long_term.recall(query)
        if key_memory:
            context_parts.append(f"[Knowledge] {key_memory}")

        context = "\n".join(context_parts)

        logger.info("[CONTEXT BUILT]")
        return context

    # =========================================================
    # KNOWLEDGE MANAGEMENT
    # =========================================================
    def remember(self, key: str, value: str):
        self.long_term.remember(key, value)

    def recall(self, key: str) -> Optional[str]:
        return self.long_term.recall(key)

    # =========================================================
    # MEMORY SEARCH
    # =========================================================
    def search(self, query: str):
        return self.long_term.search(query)

    # =========================================================
    # CLEAR SHORT-TERM MEMORY
    # =========================================================
    def clear_short_term(self):
        self.short_term_buffer.clear()
        logger.info("[SHORT-TERM CLEARED]")

    # =========================================================
    # INTELLIGENT MEMORY FILTER (ADVANCED)
    # =========================================================
    def should_store(self, message: str) -> bool:
        """
        Decide whether a message is worth storing long-term
        """
        message = message.lower()

        # Skip trivial inputs
        trivial = ["ok", "hi", "hello", "thanks"]

        if message in trivial:
            return False

        # Store meaningful content
        return True

    # =========================================================
    # SMART STORE (FILTERED)
    # =========================================================
    def smart_store(self, content: str, mem_type: str = "general"):
        if self.should_store(content):
            self.long_term.store(content, mem_type=mem_type)

    # =========================================================
    # USER PROFILE MEMORY (ADVANCED)
    # =========================================================
    def update_user_profile(self, user: str, key: str, value: str):
        """
        Example:
        ("ramesh", "favorite_language", "Python")
        """
        composite_key = f"user:{user}:{key}"
        self.long_term.remember(composite_key, value)

    def get_user_profile(self, user: str, key: str):
        composite_key = f"user:{user}:{key}"
        return self.long_term.recall(composite_key)


# =========================================================
# SINGLETON
# =========================================================
_memory_manager_instance: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    global _memory_manager_instance

    if _memory_manager_instance is None:
        _memory_manager_instance = MemoryManager()

    return _memory_manager_instance


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    mm = MemoryManager()

    mm.store_interaction("ramesh", "What is AI?", "AI is intelligence...")
    mm.remember("project", "JARVIS AI")

    context = mm.build_context("AI", "ramesh")
    print(context)