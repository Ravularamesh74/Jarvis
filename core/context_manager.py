from typing import List, Dict, Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("ContextManager")


class ContextManager:
    """
    🧠 Context Manager

    Handles:
    - Conversation history
    - Context enrichment
    - Token control
    - Session state
    """

    def __init__(self, max_history: int = 10):
        self.history: List[Dict] = []
        self.max_history = max_history
        self.state: Dict = {}

    # =============================
    # ➕ ADD MESSAGE
    # =============================
    def add(self, role: str, content: str):
        self.history.append({
            "role": role,
            "content": content,
            "time": datetime.utcnow().isoformat()
        })

        self._trim_history()

    # =============================
    # 📜 GET HISTORY
    # =============================
    def get_history(self) -> List[Dict]:
        return self.history

    # =============================
    # 🧠 ENRICH INPUT
    # =============================
    def enrich(self, user_input: str, memory_context: Optional[str] = None) -> str:
        """
        Build full prompt context
        """

        context_block = ""

        # Add recent conversation
        for msg in self.history[-self.max_history:]:
            context_block += f"{msg['role']}: {msg['content']}\n"

        # Add memory if exists
        if memory_context:
            context_block += f"\nRelevant memory:\n{memory_context}\n"

        # Final prompt
        enriched = f"""
Conversation:
{context_block}

User: {user_input}
"""

        return enriched.strip()

    # =============================
    # 🧠 STATE MANAGEMENT
    # =============================
    def set(self, key: str, value):
        self.state[key] = value

    def get(self, key: str, default=None):
        return self.state.get(key, default)

    def clear_state(self):
        self.state.clear()

    # =============================
    # ✂️ TRIM HISTORY
    # =============================
    def _trim_history(self):
        if len(self.history) > self.max_history * 2:
            self.history = self.history[-self.max_history:]

    # =============================
    # 🧹 CLEANUP
    # =============================
    def cleanup(self):
        """
        Optional periodic cleanup
        """
        self._trim_history()

    # =============================
    # 🧠 SESSION SUMMARY (ADVANCED)
    # =============================
    def summarize_context(self) -> str:
        """
        Basic summarization (can be replaced with LLM)
        """
        summary = []

        for msg in self.history[-5:]:
            summary.append(f"{msg['role']}: {msg['content']}")

        return "\n".join(summary)

    # =============================
    # 🔄 RESET SESSION
    # =============================
    def reset(self):
        logger.info("Resetting context...")
        self.history.clear()
        self.state.clear()