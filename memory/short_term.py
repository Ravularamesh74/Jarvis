"""
JARVIS Short-Term Memory (Working Memory)
----------------------------------------
Purpose:
- Maintain recent interactions (context window)
- Provide fast access to conversational state
- Support trimming, formatting, and retrieval

Design:
- In-memory ring buffer
- Structured interactions
- Context builder support
"""

import logging
from collections import deque
from typing import List, Dict, Optional

logger = logging.getLogger("JARVIS.Memory.ShortTerm")
logger.setLevel(logging.INFO)


class ShortTermMemory:
    def __init__(self, max_size: int = 20):
        """
        max_size -> number of interactions to keep
        """
        self.max_size = max_size
        self.buffer: deque = deque(maxlen=max_size)

    # =========================================================
    # ADD INTERACTION
    # =========================================================
    def add(self, user: str, message: str, response: str):
        interaction = {
            "user": user,
            "message": message,
            "response": response
        }

        self.buffer.append(interaction)
        logger.info(f"[SHORT-TERM] Added interaction for {user}")

    # =========================================================
    # GET RECENT INTERACTIONS
    # =========================================================
    def get_recent(self, limit: int = 5) -> List[Dict]:
        return list(self.buffer)[-limit:]

    # =========================================================
    # CLEAR MEMORY
    # =========================================================
    def clear(self):
        self.buffer.clear()
        logger.info("[SHORT-TERM] Cleared")

    # =========================================================
    # CONTEXT FORMATTER (VERY IMPORTANT)
    # =========================================================
    def format_context(self, limit: int = 5) -> str:
        """
        Convert memory into prompt-ready format
        """
        interactions = self.get_recent(limit)

        formatted = []
        for item in interactions:
            formatted.append(f"User: {item['message']}")
            formatted.append(f"AI: {item['response']}")

        context = "\n".join(formatted)

        logger.info("[SHORT-TERM] Context formatted")
        return context

    # =========================================================
    # LAST MESSAGE
    # =========================================================
    def last(self) -> Optional[Dict]:
        if len(self.buffer) == 0:
            return None
        return self.buffer[-1]

    # =========================================================
    # SEARCH (LIGHTWEIGHT)
    # =========================================================
    def search(self, keyword: str, limit: int = 5) -> List[Dict]:
        """
        Simple keyword search in recent memory
        """
        results = []

        for item in reversed(self.buffer):
            if keyword.lower() in item["message"].lower():
                results.append(item)
                if len(results) >= limit:
                    break

        return results

    # =========================================================
    # REMOVE LAST ENTRY
    # =========================================================
    def pop(self):
        if self.buffer:
            removed = self.buffer.pop()
            logger.info(f"[SHORT-TERM] Removed last interaction")
            return removed
        return None

    # =========================================================
    # TOKEN-AWARE TRIMMING (ADVANCED)
    # =========================================================
    def trim_by_tokens(self, max_tokens: int = 500):
        """
        Approximate token trimming (for LLM context control)
        """
        total_chars = 0
        trimmed = deque()

        # Reverse iterate to keep latest context
        for item in reversed(self.buffer):
            text = item["message"] + item["response"]
            total_chars += len(text)

            if total_chars > max_tokens:
                break

            trimmed.appendleft(item)

        self.buffer = deque(trimmed, maxlen=self.max_size)

        logger.info("[SHORT-TERM] Trimmed by token size")

    # =========================================================
    # EXPORT MEMORY (DEBUG / LOGGING)
    # =========================================================
    def dump(self) -> List[Dict]:
        return list(self.buffer)


# =========================================================
# SINGLETON (OPTIONAL)
# =========================================================
_short_term_instance: Optional[ShortTermMemory] = None


def get_short_term_memory(max_size: int = 20) -> ShortTermMemory:
    global _short_term_instance

    if _short_term_instance is None:
        _short_term_instance = ShortTermMemory(max_size)

    return _short_term_instance


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    stm = ShortTermMemory(max_size=5)

    stm.add("ramesh", "Hi", "Hello!")
    stm.add("ramesh", "What is AI?", "AI means intelligence...")

    print(stm.format_context())