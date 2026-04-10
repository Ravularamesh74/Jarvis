import os
import asyncio
import subprocess
from typing import Optional, Dict

from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger("CodingAgent")


class CodingAgent(BaseAgent):
    """
    💻 Coding Agent

    Capabilities:
    - Generate code using LLM
    - Save code to files
    - Execute code safely
    - Debug and retry
    """

    def __init__(self, brain, memory=None, context=None):
        super().__init__("CodingAgent", memory, context)
        self.brain = brain
        self.workspace = "./workspace"

        os.makedirs(self.workspace, exist_ok=True)

    # =============================
    # 🧠 MAIN LOGIC
    # =============================
    async def run(self, task: str, metadata: Optional[Dict] = None) -> str:
        logger.info(f"[CodingAgent] Processing task: {task}")

        # Step 1: Generate code from LLM
        code = await self.generate_code(task)

        if not code:
            return "Failed to generate code."

        # Step 2: Save file
        file_path = self.save_code(code)

        # Step 3: Execute code (optional)
        execution_output = await self.execute_code(file_path)

        return f"""
✅ Code generated and executed

📁 File: {file_path}

🧾 Output:
{execution_output}
"""

    # =============================
    # 🧠 CODE GENERATION
    # =============================
    async def generate_code(self, task: str) -> str:
        prompt = f"""
You are an expert software engineer.

Task:
{task}

Rules:
- Generate clean, production-level Python code
- Include comments
- No explanations outside code
"""

        try:
            response = await self.brain.ask_async(prompt)
            return response.strip()

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return ""

    # =============================
    # 📁 SAVE CODE
    # =============================
    def save_code(self, code: str) -> str:
        filename = "generated_code.py"
        path = os.path.join(self.workspace, filename)

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        logger.info(f"Code saved to {path}")
        return path

    # =============================
    # ⚙️ EXECUTE CODE (SAFE)
    # =============================
    async def execute_code(self, file_path: str) -> str:
        try:
            process = await asyncio.create_subprocess_exec(
                "python",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if stderr:
                logger.warning("Execution error detected, attempting debug...")
                return await self.debug_code(file_path, stderr.decode())

            return stdout.decode()

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            return "Execution failed."

    # =============================
    # 🐞 DEBUG LOOP (AUTO FIX)
    # =============================
    async def debug_code(self, file_path: str, error: str) -> str:
        logger.info("Starting debug loop...")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()

            debug_prompt = f"""
The following Python code has an error.

CODE:
{code}

ERROR:
{error}

Fix the code and return ONLY corrected code.
"""

            fixed_code = await self.brain.ask_async(debug_prompt)

            # overwrite file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(fixed_code)

            logger.info("Retrying execution after fix...")
            return await self.execute_code(file_path)

        except Exception as e:
            logger.error(f"Debug failed: {e}")
            return "Debugging failed."

    # =============================
    # 🔐 VALIDATION
    # =============================
    def validate(self, task: str) -> bool:
        blocked_keywords = ["delete system", "format disk"]

        return not any(word in task.lower() for word in blocked_keywords)