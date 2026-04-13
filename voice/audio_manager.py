"""
Advanced Audio Manager (JARVIS Voice Engine)
- Noise suppression
- Streaming TTS
- Voice cloning ready
"""

import pyaudio
import threading
import queue
import numpy as np

from utils.logger import get_logger
from core.event_bus import event_bus

logger = get_logger("audio_ai")


# -----------------------------------
# CONFIG
# -----------------------------------

RATE = 16000
CHUNK = 1024


# -----------------------------------
# NOISE SUPPRESSION (BASIC)
# -----------------------------------

class NoiseSuppressor:
    def process(self, audio_bytes):
        """
        Simple noise reduction (placeholder for RNNoise)
        """
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16)

        # Basic noise gate
        threshold = 500
        audio_np[np.abs(audio_np) < threshold] = 0

        return audio_np.tobytes()


# -----------------------------------
# STREAMING TTS ENGINE
# -----------------------------------

class StreamingTTS:
    def __init__(self):
        self.queue = queue.Queue()
        self.running = True

        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()

    def _worker(self):
        while self.running:
            text = self.queue.get()

            if text is None:
                break

            # Simulated streaming TTS
            for chunk in self._generate_audio(text):
                event_bus.publish("audio_out", chunk)

    def _generate_audio(self, text):
        """
        Replace with real TTS model
        """
        for char in text:
            yield char.encode()  # placeholder audio chunk

    def speak(self, text):
        self.queue.put(text)


# -----------------------------------
# VOICE CLONING (COQUI STYLE)
# -----------------------------------

class VoiceCloner:
    def __init__(self):
        self.voice_profile = None

    def load_voice(self, sample_path: str):
        """
        Load voice sample for cloning
        """
        logger.info(f"Loaded voice sample: {sample_path}")
        self.voice_profile = sample_path

    def synthesize(self, text: str):
        """
        Placeholder for cloned voice synthesis
        """
        return f"[Cloned Voice]: {text}"


# -----------------------------------
# AUDIO MANAGER
# -----------------------------------

class AudioManager:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False

        self.noise = NoiseSuppressor()
        self.tts = StreamingTTS()
        self.cloner = VoiceCloner()

    # -----------------------------------
    # START MIC STREAM
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

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            data = self.stream.read(CHUNK, exception_on_overflow=False)

            # Noise suppression
            clean = self.noise.process(data)

            # Publish cleaned audio
            event_bus.publish("audio_in", clean)

    # -----------------------------------
    # STREAMING SPEECH
    # -----------------------------------

    def speak(self, text: str, clone=False):
        logger.info(f"Speaking: {text}")

        if clone and self.cloner.voice_profile:
            text = self.cloner.synthesize(text)

        self.tts.speak(text)

    # -----------------------------------
    # STOP
    # -----------------------------------

    def stop(self):
        self.running = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()

        self.audio.terminate()