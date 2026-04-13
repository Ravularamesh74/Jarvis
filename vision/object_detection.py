"""
Advanced Object Detection System (JARVIS)
- Detection (YOLO)
- Tracking (ID persistence)
- Scene understanding
- Alert system
"""

import cv2
import numpy as np
from typing import List, Dict

from utils.logger import get_logger
from core.event_bus import event_bus

logger = get_logger("vision_ai")


# -----------------------------------
# CONFIG
# -----------------------------------

CONF_THRESHOLD = 0.4
NMS_THRESHOLD = 0.5
INPUT_SIZE = 640


# -----------------------------------
# TRACKER (CENTROID BASED)
# -----------------------------------

class Tracker:
    def __init__(self):
        self.next_id = 0
        self.objects = {}

    def update(self, detections):
        tracked = {}

        for det in detections:
            x, y, w, h = det["box"]
            cx = x + w // 2
            cy = y + h // 2

            tracked[self.next_id] = {
                "id": self.next_id,
                "centroid": (cx, cy),
                "data": det
            }
            self.next_id += 1

        self.objects = tracked
        return tracked


# -----------------------------------
# SCENE UNDERSTANDING
# -----------------------------------

class SceneAnalyzer:
    def analyze(self, objects: List[Dict]) -> Dict:
        labels = [obj["label"] for obj in objects]

        context = {
            "people_count": labels.count("person"),
            "has_phone": "cell phone" in labels,
            "has_laptop": "laptop" in labels,
            "is_vehicle_scene": any(l in labels for l in ["car", "bus", "truck"]),
        }

        # Example high-level reasoning
        if context["people_count"] > 3:
            context["scene"] = "crowded"

        elif context["has_laptop"]:
            context["scene"] = "working"

        elif context["is_vehicle_scene"]:
            context["scene"] = "traffic"

        else:
            context["scene"] = "normal"

        return context


# -----------------------------------
# ALERT SYSTEM
# -----------------------------------

class AlertSystem:
    def check(self, context: Dict, objects: List[Dict]):
        alerts = []

        # Rule-based alerts
        if context["people_count"] > 5:
            alerts.append("Crowd detected")

        if context["has_phone"]:
            alerts.append("Phone usage detected")

        if context["scene"] == "traffic":
            alerts.append("Vehicle activity detected")

        # Emit events
        for alert in alerts:
            event_bus.publish("vision_alert", alert)

        return alerts


# -----------------------------------
# OBJECT DETECTOR
# -----------------------------------

class ObjectDetector:
    def __init__(self, model_path="models/yolov5s.onnx"):
        self.net = cv2.dnn.readNet(model_path)
        self.tracker = Tracker()
        self.scene = SceneAnalyzer()
        self.alerts = AlertSystem()

    def preprocess(self, frame):
        return cv2.dnn.blobFromImage(
            frame, 1/255, (INPUT_SIZE, INPUT_SIZE),
            swapRB=True, crop=False
        )

    def detect_raw(self, frame):
        blob = self.preprocess(frame)
        self.net.setInput(blob)
        return self.net.forward()

    def postprocess(self, frame, outputs):
        h, w = frame.shape[:2]

        detections = []

        for det in outputs[0]:
            scores = det[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > CONF_THRESHOLD:
                cx, cy, bw, bh = det[:4]

                x = int((cx - bw / 2) * w)
                y = int((cy - bh / 2) * h)
                bw = int(bw * w)
                bh = int(bh * h)

                detections.append({
                    "label": str(class_id),  # map to class names if needed
                    "confidence": float(confidence),
                    "box": [x, y, bw, bh]
                })

        return detections

    # -----------------------------------
    # FULL PIPELINE
    # -----------------------------------

    def process(self, frame):
        outputs = self.detect_raw(frame)
        detections = self.postprocess(frame, outputs)

        # Tracking
        tracked = self.tracker.update(detections)

        # Scene understanding
        context = self.scene.analyze(detections)

        # Alerts
        alerts = self.alerts.check(context, detections)

        return {
            "detections": detections,
            "tracked": tracked,
            "context": context,
            "alerts": alerts
        }

    # -----------------------------------
    # DRAW
    # -----------------------------------

    def draw(self, frame, tracked):
        for obj_id, obj in tracked.items():
            x, y, w, h = obj["data"]["box"]

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"ID {obj_id}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )

        return frame