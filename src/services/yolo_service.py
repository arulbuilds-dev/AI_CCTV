import os
import time
import numpy as np
import cv2


class YOLOService:

    def __init__(self, model_path: str = "yolo11n.pt"):
        self.model_path = model_path
        self.model = None
        self.names = {}
        self.attendance_records = []
        self.face_recognizer = None
        self.face_label_map = {}
        self.face_training_ready = False
        self.rules = [
            {
                "id": "helmet_compliance",
                "name": "Helmet Compliance",
                "feature": "helmet_detection",
                "description": "Alerts when a detected person is not wearing a helmet.",
                "enabled": True,
            },
            {
                "id": "face_attendance",
                "name": "Face Recognition Attendance",
                "feature": "face_recognition",
                "description": "Recognize known faces and log attendance.",
                "enabled": True,
            },
        ]
        self.helmet_labels = {"helmet", "hardhat", "hard_hat", "safety helmet", "helmet worn"}
        self.face_confidence_threshold = 80.0

    def _load_model(self):
        if self.model is None:
            try:
                from ultralytics import YOLO
            except ImportError:
                raise RuntimeError(
                    "Ultralytics is not installed. Install ultralytics to use YOLO functionality."
                )

            print("Loading YOLO model...")
            self.model = YOLO(self.model_path)
            self.names = self.model.names
            print("YOLO model loaded.")

    def detect_frame(self, frame):
        self._load_model()
        results = self.model(frame, verbose=False)
        detections = []

        for box in results[0].boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            xyxy = box.xyxy[0]
            x1 = int(xyxy[0])
            y1 = int(xyxy[1])
            x2 = int(xyxy[2])
            y2 = int(xyxy[3])

            detections.append(
                {
                    "object": self.names.get(class_id, str(class_id)),
                    "confidence": round(confidence, 2),
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                }
            )

        return detections

    def get_features(self):
        return [
            {
                "id": "object_detection",
                "name": "Object Detection",
                "description": "Detect objects with YOLO and return bounding boxes.",
            },
            {
                "id": "face_detection",
                "name": "Face Detection",
                "description": "Detect faces using OpenCV Haar cascades.",
            },
            {
                "id": "face_recognition",
                "name": "Face Recognition",
                "description": "Recognize known faces from the face dataset and mark attendance.",
            },
            {
                "id": "helmet_detection",
                "name": "Helmet Detection",
                "description": "Check whether detected personnel are wearing helmets.",
            },
        ]

    def get_rules(self):
        return self.rules

    def add_rule(self, rule):
        if "id" not in rule or "feature" not in rule:
            return {"error": "Rule must include id and feature."}

        existing = next((r for r in self.rules if r["id"] == rule["id"]), None)
        if existing:
            existing.update(rule)
            return existing

        self.rules.append(rule)
        return rule

    def _detect_faces(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        return faces, gray

    def _prepare_face_recognizer(self):
        if self.face_training_ready:
            return

        if not hasattr(cv2, "face"):
            self.face_training_ready = False
            return

        faces_dir = os.path.join(os.getcwd(), "data", "faces")
        if not os.path.isdir(faces_dir):
            self.face_training_ready = False
            return

        samples = []
        labels = []
        label_index = 0

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        for person_name in sorted(os.listdir(faces_dir)):
            person_dir = os.path.join(faces_dir, person_name)
            if not os.path.isdir(person_dir):
                continue

            self.face_label_map[label_index] = person_name

            for image_name in sorted(os.listdir(person_dir)):
                if not image_name.lower().endswith((".jpg", ".jpeg", ".png")):
                    continue

                image_path = os.path.join(person_dir, image_name)
                image = cv2.imread(image_path)
                if image is None:
                    continue

                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                detections = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                if len(detections) == 0:
                    face_region = cv2.resize(gray_image, (200, 200))
                    samples.append(face_region)
                    labels.append(label_index)
                else:
                    for (x, y, w, h) in detections:
                        face_region = gray_image[y:y+h, x:x+w]
                        face_region = cv2.resize(face_region, (200, 200))
                        samples.append(face_region)
                        labels.append(label_index)

            label_index += 1

        if len(samples) == 0:
            self.face_training_ready = False
            return

        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_recognizer.train(np.array(samples), np.array(labels))
        self.face_training_ready = True

    def recognize_faces(self, frame):
        faces, gray = self._detect_faces(frame)
        results = []

        if not self.face_training_ready:
            self._prepare_face_recognizer()

        for (x, y, w, h) in faces:
            face_region = gray[y:y+h, x:x+w]
            face_region = cv2.resize(face_region, (200, 200))
            name = "unknown"
            confidence = None

            if self.face_training_ready and self.face_recognizer is not None:
                label, confidence = self.face_recognizer.predict(face_region)
                if confidence <= self.face_confidence_threshold:
                    name = self.face_label_map.get(label, "unknown")
                else:
                    name = "unknown"

            results.append(
                {
                    "name": name,
                    "confidence": confidence,
                    "x": x,
                    "y": y,
                    "w": w,
                    "h": h,
                }
            )

        return results

    def mark_attendance(self, recognized_faces):
        for face in recognized_faces:
            if face["name"] == "unknown":
                continue
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            record = {
                "name": face["name"],
                "confidence": face.get("confidence"),
                "timestamp": timestamp,
            }
            self.attendance_records.append(record)

    def get_attendance_records(self):
        return self.attendance_records

    def clear_attendance_records(self):
        self.attendance_records = []
        return {"status": "cleared"}

    def check_helmet_compliance(self, frame, detections=None):
        if detections is None:
            detections = self.detect_frame(frame)

        helmets = [d for d in detections if d["object"].lower() in self.helmet_labels]
        persons = [d for d in detections if d["object"].lower() == "person"]
        violations = []

        for person in persons:
            person_center_y = (person["y1"] + person["y2"]) / 2
            helmet_found = False
            for helmet in helmets:
                helmet_center_y = (helmet["y1"] + helmet["y2"]) / 2
                if helmet_center_y < person_center_y:
                    helmet_found = True
                    break

            violations.append(
                {
                    "person_box": person,
                    "helmet_found": helmet_found,
                    "status": "ok" if helmet_found else "violation",
                }
            )

        if len(persons) == 0 and len(helmets) == 0:
            return {
                "status": "unknown",
                "message": "No person or helmet evidence found. Helmet compliance cannot be determined with the current model.",
                "violations": []
            }

        return {
            "status": "ok" if all(v["helmet_found"] for v in violations) else "violation",
            "violations": violations,
            "helmet_count": len(helmets),
            "person_count": len(persons),
        }

    def annotate_frame(self, frame, object_detection: bool = True, face_recognition: bool = False, helmet_detection: bool = False, annotate: bool = True):
        detections = []
        if object_detection or helmet_detection:
            detections = self.detect_frame(frame)

        # Annotate object detections
        if annotate and detections:
            for item in detections:
                color = (0, 255, 0)
                label = item["object"]
                if helmet_detection and label.lower() in self.helmet_labels:
                    color = (255, 128, 0)
                elif label.lower() == "person":
                    color = (0, 255, 255)

                cv2.rectangle(
                    frame,
                    (item["x1"], item["y1"]),
                    (item["x2"], item["y2"]),
                    color,
                    2
                )
                cv2.putText(
                    frame,
                    f"{label} {item['confidence']:.2f}",
                    (item["x1"], max(item["y1"] - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2
                )

        # Basic face detection and recognition
        if face_recognition:
            recognized_faces = self.recognize_faces(frame)
            for face in recognized_faces:
                color = (255, 0, 0) if face["name"] == "unknown" else (0, 128, 255)
                cv2.rectangle(frame, (face["x"], face["y"]), (face["x"] + face["w"], face["y"] + face["h"]), color, 2)
                if annotate:
                    cv2.putText(
                        frame,
                        face["name"],
                        (face["x"], max(face["y"] - 10, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        color,
                        2
                    )

        return frame

    def _capture_frame(self, camera_id: int = 0):
        cap = cv2.VideoCapture(camera_id)

        if not cap.isOpened():
            return None, {"error": "Unable to open camera"}

        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            return None, {"error": "Unable to capture frame"}

        return frame, None

    def detect_from_webcam(self, camera_id: int = 0):
        frame, error = self._capture_frame(camera_id)

        if error:
            return error

        detections = self.detect_frame(frame)

        return {
            "camera_id": camera_id,
            "detections": detections
        }

    def get_object_counts(self, camera_id: int = 0):
        result = self.detect_from_webcam(camera_id)

        if "detections" not in result:
            return result

        counts = {}
        for item in result["detections"]:
            object_name = item["object"]
            counts[object_name] = counts.get(object_name, 0) + 1

        return counts

    def evaluate_compliance(self, camera_id: int = 0, helmet_compliance: bool = False, attendance: bool = False, object_detection: bool = True, face_recognition: bool = False):
        frame, error = self._capture_frame(camera_id)
        if error:
            return error

        response = {
            "camera_id": camera_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "helmet_compliance": None,
            "recognized_faces": [],
            "attendance_marked": [],
        }

        detections = []
        if object_detection or helmet_compliance:
            detections = self.detect_frame(frame)

        if helmet_compliance:
            helmet_result = self.check_helmet_compliance(frame, detections=detections)
            response["helmet_compliance"] = helmet_result

        if attendance:
            recognizable_faces = self.recognize_faces(frame)
            response["recognized_faces"] = recognizable_faces
            self.mark_attendance(recognizable_faces)
            response["attendance_marked"] = [f for f in recognizable_faces if f["name"] != "unknown"]

        if face_recognition and not attendance:
            response["recognized_faces"] = self.recognize_faces(frame)

        return response
