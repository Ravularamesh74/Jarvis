"""
Smart Listener (JARVIS Activation System)
- Custom wake word
- Face authentication
- Continuous conversation mode
"""

import time
import threading

from core.event_bus import event_bus
from utils.logger import get_logger

from voice.wake_word import WakeWordDetector
from voice.stt import AdvancedSTT
from vision.face_recognition import FaceRecognitionSystem
from utils.camera import Camera


logger = get_logger("smart_listener")


# -----------------------------------
# CONFIG
# -----------------------------------

SESSION_TIMEOUT = 10  # seconds
AUTHORIZED_USERS = ["Ramesh"]


# -----------------------------------
# SMART LISTENER
# -----------------------------------

class SmartListener:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

        # Components
        self.wake = WakeWordDetector(keywords=["jarvis"])
        self.stt = AdvancedSTT()
        self.face = FaceRecognitionSystem()
        self.camera = Camera()

        self.active = False
        self.last_active_time = 0

    # -----------------------------------
    # START SYSTEM
    # -----------------------------------

    def start(self):
        logger.info("Starting Smart Listener...")

        self.camera.start()
        self.wake.start()

        # Subscribe events
        event_bus.subscribe("wake_word_detected", self._on_wake)
        event_bus.subscribe("user_input", self._on_speech)

    # -----------------------------------
    # WAKE HANDLER
    # -----------------------------------

    def _on_wake(self, data):
        logger.info("Wake word triggered")

        frame = self.camera.get_frame()
        user = self.face.authenticate(frame)

        if user in AUTHORIZED_USERS:
            logger.info(f"Authorized user: {user}")
            self.activate()
        else:
            logger.warning("Unauthorized face detected")

    # -----------------------------------
    # ACTIVATE SYSTEM
    # -----------------------------------

    def activate(self):
        self.active = True
        self.last_active_time = time.time()

        logger.info("JARVIS Activated")

        # Start STT if not running
        self.stt.start()

        event_bus.publish("jarvis_activated", {})

    # -----------------------------------
    # HANDLE SPEECH
    # -----------------------------------

    def _on_speech(self, data):
        if not self.active:
            return

        # Support both string or dict input
        text = data["text"] if isinstance(data, dict) else data

        logger.info(f"Processing: {text}")

        self.last_active_time = time.time()

        response = self.orchestrator.handle(text)

        event_bus.publish("ai_response", response)

    # -----------------------------------
    # CONTINUOUS MODE LOOP
    # -----------------------------------

    def run(self):
        """
        Keeps session alive until timeout
        """
        while True:
            if self.active:
                if time.time() - self.last_active_time > SESSION_TIMEOUT:
                    self.deactivate()

            time.sleep(1)

    # -----------------------------------
    # DEACTIVATE
    # -----------------------------------

    def deactivate(self):
        logger.info("JARVIS going to sleep")

        self.active = False
        event_bus.publish("jarvis_sleep", {})