"""
Advanced Vision System for JARVIS
- Face Recognition
- Object Detection (YOLO)
- Gesture Control (MediaPipe)
"""

import cv2
import face_recognition
import numpy as np
import mediapipe as mp

from utils.logger import get_logger

logger = get_logger("vision")


# -----------------------------------
# CAMERA
# -----------------------------------

class Camera:
    def __init__(self, index=0):
        self.cap = cv2.VideoCapture(index)

    def read(self):
        ret, frame = self.cap.read()
        return frame if ret else None

    def release(self):
        self.cap.release()


# -----------------------------------
# FACE RECOGNITION
# -----------------------------------

class FaceRecognition:
    def __init__(self):
        self.known_encodings = []
        self.known_names = []

    def add_face(self, image_path: str, name: str):
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]

        self.known_encodings.append(encoding)
        self.known_names.append(name)

    def recognize(self, frame):
        rgb = frame[:, :, ::-1]

        locations = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, locations)

        results = []

        for encoding, loc in zip(encodings, locations):
            matches = face_recognition.compare_faces(self.known_encodings, encoding)
            name = "Unknown"

            if True in matches:
                idx = matches.index(True)
                name = self.known_names[idx]

            results.append((name, loc))

        return results


# -----------------------------------
# OBJECT DETECTION (YOLOv5/8 via OpenCV DNN)
# -----------------------------------

class ObjectDetector:
    def __init__(self, model_path="yolov5s.onnx"):
        self.net = cv2.dnn.readNet(model_path)

    def detect(self, frame):
        blob = cv2.dnn.blobFromImage(frame, 1/255, (640, 640), swapRB=True)
        self.net.setInput(blob)
        outputs = self.net.forward()

        # Simplified: return raw outputs (you can decode boxes)
        return outputs


# -----------------------------------
# GESTURE CONTROL (HAND TRACKING)
# -----------------------------------

class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands()
        self.mp_draw = mp.solutions.drawing_utils

    def detect(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands.process(rgb)

        gestures = []

        if result.multi_hand_landmarks:
            for hand in result.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand)

                # Example gesture: count fingers
                landmarks = hand.landmark
                if landmarks[8].y < landmarks[6].y:
                    gestures.append("pointing")

        return gestures


# -----------------------------------
# UNIFIED VISION SYSTEM
# -----------------------------------

class VisionSystem:
    def __init__(self):
        self.camera = Camera()
        self.face = FaceRecognition()
        self.object = ObjectDetector()
        self.gesture = GestureController()

    def process_frame(self):
        frame = self.camera.read()
        if frame is None:
            return None

        # Face recognition
        faces = self.face.recognize(frame)

        # Object detection
        objects = self.object.detect(frame)

        # Gesture detection
        gestures = self.gesture.detect(frame)

        return {
            "frame": frame,
            "faces": faces,
            "objects": objects,
            "gestures": gestures
        }

    def release(self):
        self.camera.release()