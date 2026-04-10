import os
import json
from typing import List, Dict, Optional
from datetime import datetime

from utils.logger import get_logger

logger = get_logger("Memory")


class Memory:
    """
    🧠 Hybrid Memory System

    Features:
    - Short-term memory (recent interactions)
    - Long-term storage (JSON DB)
    - Semantic-ready (future vector DB)
    """

    def __init__(self, path: str = "./data/memory.json", max_short: int = 20):
        self.path = path
        self.max_short = max_short

        self.short_term: List[Dict] = []
        self.long_term: List[Dict] = self._load()

    # =============================
    # ➕ STORE MEMORY
    # =============================
    def store(self, user: str, response: str):
        record = {
            "user": user,
            "response": response,
            "time": datetime.utcnow().isoformat()
        }

        # short-term
        self.short_term.append(record)
        self._trim_short()

        # long-term
        self.long_term.append(record)
        self._save()

        logger.info("Memory stored")

    # =============================
    # 🔍 RETRIEVE MEMORY
    # =============================
    def retrieve(self, query: str, top_k: int = 3) -> str:
        """
        Simple keyword-based retrieval
        (upgrade to vector later)
        """

        if not self.long_term:
            return ""

        query = query.lower()

        scored = []
        for item in self.long_term:
            score = self._score(query, item)
            if score > 0:
                scored.append((score, item))

        scored.sort(reverse=True, key=lambda x: x[0])

        results = [item for _, item in scored[:top_k]]

        return self._format(results)

    # =============================
    # 🧠 SCORING FUNCTION
    # =============================
    def _score(self, query: str, item: Dict) -> int:
        text = f"{item['user']} {item['response']}".lower()
        return sum(1 for word in query.split() if word in text)

    # =============================
    # 🧾 FORMAT MEMORY
    # =============================
    def _format(self, items: List[Dict]) -> str:
        output = ""

        for item in items:
            output += f"User: {item['user']}\n"
            output += f"Assistant: {item['response']}\n\n"

        return output.strip()

    # =============================
    # 💾 LOAD MEMORY
    # =============================
    def _load(self) -> List[Dict]:
        if not os.path.exists(self.path):
            return []

        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)

        except Exception as e:
            logger.error(f"Memory load failed: {e}")
            return []

    # =============================
    # 💾 SAVE MEMORY
    # =============================
    def _save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)

            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.long_term, f, indent=2)

        except Exception as e:
            logger.error(f"Memory save failed: {e}")

    # =============================
    # ✂️ TRIM SHORT MEMORY
    # =============================
    def _trim_short(self):
        if len(self.short_term) > self.max_short:
            self.short_term = self.short_term[-self.max_short:]

    # =============================
    # 🧹 CLEAR MEMORY
    # =============================
    def clear(self):
        self.short_term.clear()
        self.long_term.clear()
        self._save()

    # =============================
    # 📊 MEMORY STATS
    # =============================
    def stats(self) -> Dict:
        return {
            "short_term": len(self.short_term),
            "long_term": len(self.long_term)
        }