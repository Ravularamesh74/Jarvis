"""
Wake Word Detection System for JARVIS
- Offline detection (Porcupine)
- Multi-keyword support
- Event-driven activation
"""

import pvporcupine
import pyaudio
import struct
import threading

from utils.logger import get_logger
from core.event_bus import event_bus

logger = get_logger("wake_word")


# -----------------------------------
# CONFIG
# -----------------------------------

DEFAULT_KEYWORDS = ["jarvis"]


# -----------------------------------
# WAKE WORD DETECTOR
# -----------------------------------

class WakeWordDetector:
    def __init__(self, keywords=None, sensitivity=0.6):
        self.keywords = keywords or DEFAULT_KEYWORDS

        logger.info(f"Loading wake words: {self.keywords}")

        self.porcupine = pvporcupine.create(
            keywords=self.keywords,
            sensitivities=[sensitivity] * len(self.keywords)
        )

        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(
            rate=self.porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=self.porcupine.frame_length
        )

        self.running = False

    # -----------------------------------
    # START LISTENING
    # -----------------------------------

    def start(self):
        logger.info("Wake word detection started")

        self.running = True

        thread = threading.Thread(target=self._loop, daemon=True)
        thread.start()

    # -----------------------------------
    # MAIN LOOP
    # -----------------------------------

    def _loop(self):
        while self.running:
            pcm = self.stream.read(
                self.porcupine.frame_length,
                exception_on_overflow=False
            )

            pcm = struct.unpack_from(
                "h" * self.porcupine.frame_length,
                pcm
            )

            keyword_index = self.porcupine.process(pcm)

            if keyword_index >= 0:
                keyword = self.keywords[keyword_index]

                logger.info(f"Wake word detected: {keyword}")

                # Emit event
                event_bus.publish("wake_word_detected", {
                    "keyword": keyword
                })

    # -----------------------------------
    # STOP
    # -----------------------------------

    def stop(self):
        logger.info("Stopping wake word detector")

        self.running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.audio.terminate()
        self.porcupine.delete()