"""
Cinematic TTS System (JARVIS)
- Coqui XTTS v2 integration
- Voice cloning
- Prosody control
- Multi-speaker switching
"""

import threading
import queue
import numpy as np
import pyaudio

from TTS.api import TTS

from utils.logger import get_logger
from core.event_bus import event_bus

logger = get_logger("tts_xtts")


# -----------------------------------
# CONFIG
# -----------------------------------

RATE = 24000
CHUNK = 1024


# -----------------------------------
# MULTI-SPEAKER MANAGER
# -----------------------------------

class SpeakerManager:
    def __init__(self):
        self.voices = {}  # name -> sample path

    def add_voice(self, name: str, sample_path: str):
        self.voices[name] = sample_path

    def get_voice(self, name: str):
        return self.voices.get(name)


# -----------------------------------
# PROSODY ENGINE
# -----------------------------------

class Prosody:
    def __init__(self):
        self.speed = 1.0
        self.pitch = 1.0
        self.emotion = "neutral"

    def apply(self, text: str):
        """
        Modify text or parameters based on emotion
        """
        if self.emotion == "excited":
            text = text + "!!!"
        elif self.emotion == "calm":
            text = text.lower()

        return text


# -----------------------------------
# XTTS ENGINE
# -----------------------------------

class XTTS_Engine:
    def __init__(self):
        logger.info("Loading XTTS v2 model...")
        self.tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

    def synthesize(self, text, speaker_wav=None, language="en"):
        """
        Generate waveform using XTTS
        """
        wav = self.tts.tts(
            text=text,
            speaker_wav=speaker_wav,
            language=language
        )
        return np.array(wav, dtype=np.float32)


# -----------------------------------
# STREAMING PLAYER
# -----------------------------------

class AudioPlayer:
    def __init__(self):
        self.audio = pyaudio.PyAudio()

        self.stream = self.audio.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=RATE,
            output=True
        )

    def play(self, audio_np):
        for i in range(0, len(audio_np), CHUNK):
            chunk = audio_np[i:i+CHUNK]
            self.stream.write(chunk.tobytes())

            event_bus.publish("audio_out", chunk.tobytes())

    def close(self):
        self.stream.close()
        self.audio.terminate()


# -----------------------------------
# MAIN TTS SYSTEM
# -----------------------------------

class TextToSpeech:
    def __init__(self):
        self.engine = XTTS_Engine()
        self.player = AudioPlayer()
        self.speakers = SpeakerManager()
        self.prosody = Prosody()

        self.queue = queue.Queue()
        self.running = True

        threading.Thread(target=self._worker, daemon=True).start()

    # -----------------------------------
    # WORKER LOOP
    # -----------------------------------

    def _worker(self):
        while self.running:
            item = self.queue.get()

            if item is None:
                break

            text, speaker, lang = item

            # Apply prosody
            text = self.prosody.apply(text)

            speaker_wav = self.speakers.get_voice(speaker)

            audio = self.engine.synthesize(
                text,
                speaker_wav=speaker_wav,
                language=lang
            )

            self.player.play(audio)

    # -----------------------------------
    # SPEAK
    # -----------------------------------

    def speak(self, text: str, speaker="default", language="en"):
        logger.info(f"[{speaker}] {text}")
        self.queue.put((text, speaker, language))

    # -----------------------------------
    # ADD VOICE PROFILE
    # -----------------------------------

    def add_voice(self, name: str, sample_path: str):
        self.speakers.add_voice(name, sample_path)

    # -----------------------------------
    # CONTROL PROSODY
    # -----------------------------------

    def set_emotion(self, emotion: str):
        self.prosody.emotion = emotion

    def stop(self):
        self.running = False
        self.queue.put(None)
        self.player.close()