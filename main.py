import asyncio
import signal
import uuid
from datetime import datetime

# Core systems
from core.orchestrator import Orchestrator
from core.context_manager import ContextManager

# Voice
from voice.audio_manager import VoiceStream

# Memory
from memory.memory_manager import MemoryManager

# Utils
from utils.logger import get_logger

# Optional: local fallback LLM
USE_LOCAL_FALLBACK = True

logger = get_logger("JARVIS")

class JarvisRuntime:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.running = True

        logger.info(f"🚀 Booting JARVIS | Session: {self.session_id}")

        # Core components
        self.context = ContextManager()
        self.memory = MemoryManager()
        self.orchestrator = Orchestrator(memory=self.memory, context=self.context)

        # Voice stream (real-time)
        self.voice = VoiceStream()

        # Async queues (event-driven pipeline)
        self.input_queue = asyncio.Queue()
        self.output_queue = asyncio.Queue()

    # -----------------------------
    # 🎙️ INPUT PIPELINE (STT STREAM)
    # -----------------------------
    async def capture_voice(self):
        async for chunk in self.voice.listen_stream():
            if not self.running:
                break

            if chunk:
                await self.input_queue.put({
                    "type": "voice",
                    "data": chunk,
                    "timestamp": datetime.utcnow()
                })

    # -----------------------------
    # 🧠 PROCESS PIPELINE (BRAIN)
    # -----------------------------
    async def process_events(self):
        while self.running:
            event = await self.input_queue.get()

            try:
                if event["type"] == "voice":
                    user_text = event["data"]

                    logger.info(f"🧑 User: {user_text}")

                    # Inject memory context
                    memory_context = self.memory.retrieve(user_text)
                    enriched_input = self.context.enrich(user_text, memory_context)

                    # Main AI execution
                    response = await self.safe_ai_call(enriched_input)

                    # Store memory
                    self.memory.store(user_text, response)

                    await self.output_queue.put({
                        "type": "response",
                        "data": response
                    })

            except Exception as e:
                logger.error(f"Processing error: {e}")

    # -----------------------------
    # 🤖 AI CALL (with fallback)
    # -----------------------------
    async def safe_ai_call(self, prompt):
        try:
            return await self.orchestrator.handle_async(prompt)

        except Exception as e:
            logger.warning(f"⚠️ Primary LLM failed: {e}")

            if USE_LOCAL_FALLBACK:
                logger.info("🔁 Switching to local fallback (Ollama)")
                return await self.orchestrator.handle_local(prompt)

            return "Something went wrong."

    # -----------------------------
    # 🔊 OUTPUT PIPELINE (TTS)
    # -----------------------------
    async def output_voice(self):
        while self.running:
            event = await self.output_queue.get()

            if event["type"] == "response":
                response = event["data"]

                logger.info(f"🤖 Jarvis: {response}")

                await self.voice.speak_stream(response)

    # -----------------------------
    # 🧠 BACKGROUND TASKS
    # -----------------------------
    async def background_tasks(self):
        while self.running:
            # Periodic memory optimization
            self.memory.optimize()

            # Context cleanup
            self.context.cleanup()

            await asyncio.sleep(10)

    # -----------------------------
    # 🛑 SHUTDOWN HANDLER
    # -----------------------------
    def shutdown(self):
        logger.info("🛑 Shutting down JARVIS...")
        self.running = False

    # -----------------------------
    # 🚀 MAIN RUNTIME
    # -----------------------------
    async def run(self):
        loop = asyncio.get_event_loop()

        # Graceful shutdown
        loop.add_signal_handler(signal.SIGINT, self.shutdown)
        loop.add_signal_handler(signal.SIGTERM, self.shutdown)

        tasks = [
            asyncio.create_task(self.capture_voice()),
            asyncio.create_task(self.process_events()),
            asyncio.create_task(self.output_voice()),
            asyncio.create_task(self.background_tasks()),
        ]

        await asyncio.gather(*tasks)


# -----------------------------
# 🧠 ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    jarvis = JarvisRuntime()

    try:
        asyncio.run(jarvis.run())
    except KeyboardInterrupt:
        jarvis.shutdown()