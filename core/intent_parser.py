from typing import Dict, Any
from utils.logger import get_logger

logger = get_logger("IntentParser")


class IntentParser:
    """
    🧠 Hybrid Intent Parser

    Strategy:
    1. Rule-based detection (fast)
    2. LLM fallback (accurate)
    """

    def __init__(self, brain=None):
        self.brain = brain

        # 🔥 Keyword mapping
        self.rules = {
            "code": ["code", "program", "script", "python", "build app"],
            "research": ["what is", "who is", "latest", "news", "explain"],
            "automation": ["open", "run", "execute", "system", "shutdown"],
            "plan": ["build", "create project", "develop", "end-to-end"],
        }

    # =============================
    # 🚀 MAIN ENTRY
    # =============================
    async def parse(self, task: str) -> Dict[str, Any]:
        task_lower = task.lower()

        # Step 1: Rule-based detection
        intent, confidence = self.rule_based(task_lower)

        if confidence > 0.7:
            return {
                "intent": intent,
                "confidence": confidence,
                "source": "rule"
            }

        # Step 2: LLM fallback
        if self.brain:
            return await self.llm_based(task)

        # Default fallback
        return {
            "intent": "automation",
            "confidence": 0.5,
            "source": "default"
        }

    # =============================
    # ⚡ RULE-BASED DETECTION
    # =============================
    def rule_based(self, task: str):
        scores = {}

        for intent, keywords in self.rules.items():
            score = sum(1 for word in keywords if word in task)
            scores[intent] = score

        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]

        # Normalize confidence
        confidence = min(max_score / 3, 1.0)

        return best_intent, confidence

    # =============================
    # 🧠 LLM FALLBACK
    # =============================
    async def llm_based(self, task: str) -> Dict[str, Any]:
        prompt = f"""
Classify this task into one:

- plan
- code
- research
- automation

Task:
{task}

Return JSON:
{{
  "intent": "...",
  "confidence": 0.0-1.0
}}
"""

        try:
            result = await self.brain.ask_json(prompt)

            return {
                "intent": result.get("intent", "automation"),
                "confidence": result.get("confidence", 0.6),
                "source": "llm"
            }

        except Exception as e:
            logger.error(f"LLM intent failed: {e}")

            return {
                "intent": "automation",
                "confidence": 0.5,
                "source": "fallback"
            }