"""
Advanced Face Recognition System (JARVIS)
- FAISS vector search
- Multi-user tracking
- Anti-spoof detection
"""

import face_recognition
import numpy as np
import faiss
import cv2
from typing import List, Dict

from utils.logger import get_logger

logger = get_logger("face_ai")


# -----------------------------------
# CONFIG
# -----------------------------------

DIM = 128  # face encoding size
THRESHOLD = 0.5


# -----------------------------------
# FACE DATABASE (FAISS)
# -----------------------------------

class FaceDB:
    def __init__(self):
        self.index = faiss.IndexFlatL2(DIM)
        self.names: List[str] = []

    def add(self, encoding: np.ndarray, name: str):
        self.index.add(np.array([encoding]).astype("float32"))
        self.names.append(name)

    def search(self, encoding: np.ndarray):
        if self.index.ntotal == 0:
            return None

        D, I = self.index.search(
            np.array([encoding]).astype("float32"),
            k=1
        )

        if D[0][0] < THRESHOLD:
            return self.names[I[0][0]]

        return "Unknown"


# -----------------------------------
# TRACKING SYSTEM
# -----------------------------------

class Tracker:
    def __init__(self):
        self.next_id = 0
        self.objects: Dict[int, tuple] = {}

    def update(self, detections):
        """
        detections: list of (x, y, w, h)
        """
        tracked = {}

        for det in detections:
            tracked[self.next_id] = det
            self.next_id += 1

        self.objects = tracked
        return tracked


# -----------------------------------
# ANTI-SPOOF (BASIC)
# -----------------------------------

class AntiSpoof:
    def __init__(self):
        self.prev_frame = None

    def is_real(self, frame):
        """
        Simple motion-based liveness check
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.prev_frame is None:
            self.prev_frame = gray
            return False

        diff = cv2.absdiff(self.prev_frame, gray)
        self.prev_frame = gray

        movement = np.sum(diff)

        return movement > 50000  # threshold


# -----------------------------------
# MAIN SYSTEM
# -----------------------------------

class FaceRecognitionSystem:
    def __init__(self):
        self.db = FaceDB()
        self.tracker = Tracker()
        self.spoof = AntiSpoof()

    # -----------------------------------
    # ADD USER
    # -----------------------------------

    def add_face(self, image_path: str, name: str):
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]

        self.db.add(encoding, name)
        logger.info(f"Added user: {name}")

    # -----------------------------------
    # PROCESS FRAME
    # -----------------------------------

    def process(self, frame):
        rgb = frame[:, :, ::-1]

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        results = []

        for encoding, (top, right, bottom, left) in zip(encodings, locations):
            name = self.db.search(encoding)

            # Anti-spoof check
            is_real = self.spoof.is_real(frame)

            if not is_real:
                name = "Spoof Detected"

            results.append({
                "name": name,
                "box": (top, right, bottom, left)
            })

        # Tracking
        boxes = [(l, t, r - l, b - t) for (t, r, b, l) in locations]
        tracked = self.tracker.update(boxes)

        return {
            "faces": results,
            "tracked": tracked
        }