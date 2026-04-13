"""
Advanced STT System (JARVIS)
- Whisper streaming
- Speaker identification
- Multilingual detection
"""

import queue
import threading
import numpy as np
import pyaudio

import whisper
from pyannote.audio import Pipeline

from utils.logger import get_logger
from core.event_bus import event_bus

logger = get_logger("stt_ai")


# -----------------------------------
# CONFIG
# -----------------------------------

RATE = 16000
CHUNK = 1024
MODEL_SIZE = "base"  # tiny | base | small | medium | large


# -----------------------------------
# STT ENGINE
# -----------------------------------

class AdvancedSTT:
    def __init__(self):
        logger.info("Loading Whisper model...")
        self.model = whisper.load_model(MODEL_SIZE)

        logger.info("Loading speaker identification...")
        self.speaker_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization"
        )

        self.audio = pyaudio.PyAudio()
        self.stream = None

        self.queue = queue.Queue()
        self.running = False

    # -----------------------------------
    # START STREAM
    # -----------------------------------

    def start(self):
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )

        self.running = True

        threading.Thread(target=self._capture_loop, daemon=True).start()
        threading.Thread(target=self._process_loop, daemon=True).start()

    # -----------------------------------
    # CAPTURE AUDIO
    # -----------------------------------

    def _capture_loop(self):
        while self.running:
            data = self.stream.read(CHUNK, exception_on_overflow=False)
            self.queue.put(data)

    # -----------------------------------
    # PROCESS AUDIO
    # -----------------------------------

    def _process_loop(self):
        buffer = []

        while self.running:
            if self.queue.empty():
                continue

            data = self.queue.get()
            buffer.append(data)

            # Process every ~2 seconds
            if len(buffer) > (RATE / CHUNK * 2):
                audio_bytes = b"".join(buffer)
                buffer.clear()

                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

                # -----------------------------------
                # WHISPER TRANSCRIPTION
                # -----------------------------------

                result = self.model.transcribe(
                    audio_np,
                    language=None,  # auto-detect
                    fp16=False
                )

                text = result.get("text", "").strip()
                language = result.get("language", "unknown")

                if text:
                    logger.info(f"[{language}] {text}")

                    # -----------------------------------
                    # SPEAKER IDENTIFICATION
                    # -----------------------------------

                    speaker = self.identify_speaker(audio_np)

                    # Publish event
                    event_bus.publish("user_input", {
                        "text": text,
                        "speaker": speaker,
                        "language": language
                    })

    # -----------------------------------
    # SPEAKER IDENTIFICATION
    # -----------------------------------

    def identify_speaker(self, audio_np):
        try:
            diarization = self.speaker_pipeline(audio_np)

            for turn, _, speaker in diarization.itertracks(yield_label=True):
                return speaker

        except Exception as e:
            logger.warning(f"Speaker ID failed: {e}")

        return "unknown"

    # -----------------------------------
    # STOP
    # -----------------------------------

    def stop(self):
        self.running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.audio.terminate()