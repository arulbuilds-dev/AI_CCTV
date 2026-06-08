import cv2
from ultralytics import YOLO


class YOLOService:

    def __init__(self, model_path: str = "yolo11n.pt"):
        print("Loading YOLO model...")
        self.model = YOLO(model_path)
        self.names = self.model.names
        print("YOLO model loaded.")

    def detect_frame(self, frame):
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
                    "object": self.names[class_id],
                    "confidence": round(confidence, 2),
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            )

        return detections

    def annotate_frame(self, frame):
        detections = self.detect_frame(frame)

        for item in detections:
            cv2.rectangle(
                frame,
                (item["x1"], item["y1"]),
                (item["x2"], item["y2"]),
                (0, 255, 0),
                2
            )
            cv2.putText(
                frame,
                f"{item['object']} {item['confidence']:.2f}",
                (item["x1"], max(item["y1"] - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
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
