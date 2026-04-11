"""
JARVIS WhatsApp Integration Layer
--------------------------------
Capabilities:
- Send instant + scheduled messages
- Command routing to brain
- Async execution
- Session tracking
- Extendable to webhook / Cloud API

Dependencies:
    pip install pywhatkit

Future Upgrade:
    WhatsApp Cloud API (recommended for production)
"""

import pywhatkit as kit
import threading
import datetime
import logging
from typing import Optional, Dict

logger = logging.getLogger("JARVIS.WhatsApp")
logger.setLevel(logging.INFO)


class WhatsAppClient:
    def __init__(self, brain=None, memory=None, scheduler=None):
        """
        brain      -> command execution engine (brain.py)
        memory     -> memory manager (memory.py)
        scheduler  -> task scheduler (scheduler.py)
        """
        self.brain = brain
        self.memory = memory
        self.scheduler = scheduler

        self.sessions: Dict[str, dict] = {}

    # =========================================================
    # CORE: SEND MESSAGE
    # =========================================================
    def send(self, phone: str, message: str, wait_time: int = 10):
        """
        Send WhatsApp message instantly
        """
        try:
            logger.info(f"[SEND] -> {phone}: {message}")

            kit.sendwhatmsg_instantly(
                phone_no=phone,
                message=message,
                wait_time=wait_time,
                tab_close=True,
                close_time=3
            )

        except Exception as e:
            logger.error(f"[ERROR] Send failed: {e}")

    # =========================================================
    # ASYNC SEND
    # =========================================================
    def send_async(self, phone: str, message: str):
        thread = threading.Thread(target=self.send, args=(phone, message))
        thread.daemon = True
        thread.start()

    # =========================================================
    # SCHEDULE MESSAGE
    # =========================================================
    def schedule(self, phone: str, message: str, send_time: datetime.datetime):
        """
        Schedule message via scheduler OR fallback to pywhatkit
        """
        if self.scheduler:
            self.scheduler.add_task(
                func=self.send,
                run_at=send_time,
                args=(phone, message)
            )
        else:
            try:
                kit.sendwhatmsg(
                    phone,
                    message,
                    send_time.hour,
                    send_time.minute
                )
            except Exception as e:
                logger.error(f"[ERROR] Schedule failed: {e}")

    # =========================================================
    # INCOMING MESSAGE ENTRY POINT (IMPORTANT)
    # =========================================================
    def receive(self, phone: str, message: str):
        """
        Entry point for incoming messages (Webhook / future)
        """
        logger.info(f"[RECEIVED] {phone}: {message}")

        # Store memory
        if self.memory:
            self.memory.store("whatsapp", phone, message)

        # Start session if not exists
        if phone not in self.sessions:
            self._start_session(phone)

        # Route message
        self._route(phone, message)

    # =========================================================
    # ROUTER
    # =========================================================
    def _route(self, phone: str, message: str):
        message = message.strip()

        if message.lower().startswith("jarvis"):
            self._handle_command(phone, message)
        else:
            self._handle_normal_message(phone, message)

    # =========================================================
    # COMMAND HANDLER
    # =========================================================
    def _handle_command(self, phone: str, message: str):
        if not self.brain:
            self.send_async(phone, "⚠️ Brain not connected.")
            return

        try:
            logger.info(f"[COMMAND] {message}")

            response = self.brain.execute(message)

            if response:
                self.send_async(phone, response)

        except Exception as e:
            logger.error(f"[ERROR] Command failed: {e}")
            self.send_async(phone, "Error processing command.")

    # =========================================================
    # NORMAL MESSAGE HANDLER
    # =========================================================
    def _handle_normal_message(self, phone: str, message: str):
        logger.info(f"[NORMAL] {phone}: {message}")

        # Optional: auto-reply logic
        if self.brain:
            try:
                reply = self.brain.chat(message)
                if reply:
                    self.send_async(phone, reply)
            except Exception as e:
                logger.error(f"[ERROR] Chat failed: {e}")

    # =========================================================
    # SESSION MANAGEMENT
    # =========================================================
    def _start_session(self, phone: str):
        self.sessions[phone] = {
            "started_at": datetime.datetime.now(),
            "messages": []
        }
        logger.info(f"[SESSION STARTED] {phone}")

    def end_session(self, phone: str):
        if phone in self.sessions:
            logger.info(f"[SESSION ENDED] {phone}")
            del self.sessions[phone]

    # =========================================================
    # CONTACT HELPER
    # =========================================================
    def send_to_contact(self, name: str, message: str):
        """
        Requires memory/contact store
        """
        if not self.memory:
            raise ValueError("Memory system required for contact lookup")

        phone = self.memory.get_contact(name)

        if not phone:
            raise ValueError(f"Contact '{name}' not found")

        self.send_async(phone, message)


# =========================================================
# SINGLETON (OPTIONAL)
# =========================================================
_whatsapp_instance: Optional[WhatsAppClient] = None


def get_whatsapp_client(**kwargs) -> WhatsAppClient:
    global _whatsapp_instance
    if _whatsapp_instance is None:
        _whatsapp_instance = WhatsAppClient(**kwargs)
    return _whatsapp_instance


# =========================================================
# TEST MODE
# =========================================================
if __name__ == "__main__":
    class DummyBrain:
        def execute(self, cmd):
            return f"Executed: {cmd}"

        def chat(self, msg):
            return f"Echo: {msg}"

    client = WhatsAppClient(brain=DummyBrain())

    PHONE = "+919640059577"

    client.send_async(PHONE, "🚀 JARVIS WhatsApp module active")