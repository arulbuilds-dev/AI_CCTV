# from ultralytics import YOLO

# class YOLOService:

#     def __init__(self):
#         self.model = YOLO("yolo11n.pt")

#     def detect(self, frame):

#         results = self.model(frame)

#         detections = []

#         for box in results[0].boxes:

#             detections.append({
#                 "class_id": int(box.cls[0]),
#                 "confidence": float(box.conf[0])
#             })

#         return detections

import cv2
from ultralytics import YOLO


class YOLOService:

    def __init__(self):
        print("Loading YOLO model...")
        self.model = YOLO("yolo11n.pt")
        print("YOLO model loaded.")

    def get_object_counts(self):
        result = self.detect_from_webcam()

        if "detections" not in result:
            return result

        counts = {}

        for item in result["detections"]:

            object_name = item["object"]

            counts[object_name] = (
                counts.get(object_name, 0) + 1
            )

        return counts

    def detect_from_webcam(self):

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return {
                "error": "Unable to open webcam"
            }

        ret, frame = cap.read()

        cap.release()

        if not ret:
            return {
                "error": "Unable to capture frame"
            }

        results = self.model(frame, verbose=False)

        detections = []

        names = self.model.names

        for box in results[0].boxes:

            class_id = int(box.cls[0])
            confidence = float(box.conf[0])

            # detections.append(
            #     {
            #         "object": names[class_id],
            #         "confidence": round(confidence, 2)
            #     }
            # )

            xyxy = box.xyxy[0]

            x1 = int(xyxy[0])
            y1 = int(xyxy[1])
            x2 = int(xyxy[2])
            y2 = int(xyxy[3])

            detections.append(
                {
                    "object": names[class_id],
                    "confidence": round(confidence, 2),
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2
                }
            )

        return {
            "camera_id": 0,
            "detections": detections
        }