import os
import json
import asyncio
from typing import Optional, List, Dict, Any

from openai import AsyncOpenAI
from utils.logger import get_logger

logger = get_logger("Brain")


class Brain:
    """
    🧠 Brain (LLM Engine)

    Features:
    - Async + sync support
    - Context-aware responses
    - JSON-safe outputs
    - Fallback to local LLM (Ollama)
    """

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1")

        self.client = AsyncOpenAI(api_key=self.api_key)

        # Local fallback config
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

    # =============================
    # 🚀 MAIN ENTRY (ASYNC)
    # =============================
    async def ask_async(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        messages = self._build_messages(prompt, system)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"OpenAI failed: {e}")
            return await self._fallback_ollama(prompt)

    # =============================
    # ⚡ SYNC WRAPPER
    # =============================
    def ask(self, prompt: str) -> str:
        return asyncio.run(self.ask_async(prompt))

    # =============================
    # 🧠 MESSAGE BUILDER
    # =============================
    def _build_messages(self, prompt: str, system: Optional[str]) -> List[Dict]:
        messages = []

        if system:
            messages.append({"role": "system", "content": system})

        messages.append({"role": "user", "content": prompt})

        return messages

    # =============================
    # 🔁 LOCAL FALLBACK (OLLAMA)
    # =============================
    async def _fallback_ollama(self, prompt: str) -> str:
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=30,
                )

                data = response.json()
                return data.get("response", "")

        except Exception as e:
            logger.error(f"Ollama fallback failed: {e}")
            return "Both primary and fallback models failed."

    # =============================
    # 🧾 JSON SAFE RESPONSE
    # =============================
    async def ask_json(self, prompt: str) -> Dict[str, Any]:
        """
        Ensures valid JSON output
        """

        json_prompt = f"""
Return ONLY valid JSON.

{prompt}
"""

        response = await self.ask_async(json_prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON, retrying...")

            # retry once
            retry_prompt = f"""
Fix this into valid JSON:

{response}
"""
            fixed = await self.ask_async(retry_prompt)

            try:
                return json.loads(fixed)
            except:
                return {"error": "Invalid JSON response"}

    # =============================
    # 🌊 STREAMING (OPTIONAL)
    # =============================
    async def stream(self, prompt: str):
        messages = self._build_messages(prompt, None)

        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Streaming failed: {e}")
            yield "Streaming error."

    # =============================
    # 🧠 INTENT CLASSIFIER
    # =============================
    async def classify(self, task: str) -> str:
        prompt = f"""
Classify the task:

Options:
- plan
- code
- research
- automation

Task:
{task}

Return one word.
"""
        return (await self.ask_async(prompt)).strip().lower()

    # =============================
    # 🧠 SUMMARIZER
    # =============================
    async def summarize(self, text: str) -> str:
        prompt = f"""
Summarize this:

{text}
"""
        return await self.ask_async(prompt)

    # =============================
    # 🧠 PLANNER HELPER
    # =============================
    async def generate_plan(self, task: str):
        prompt = f"""
Break task into steps in JSON:

Task:
{task}

Format:
[
  {{"step": 1, "action": "...", "agent": "..."}}
]
"""
        return await self.ask_json(prompt)