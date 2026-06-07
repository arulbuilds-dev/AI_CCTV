import cv2
from ultralytics import YOLO

print("Loading model...")
model = YOLO("yolo11n.pt")

print("Opening webcam...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open webcam")
    exit()

while True:
    ret, frame = cap.read()

    if not ret:
        break

    results = model(frame, verbose=False)

    annotated_frame = results[0].plot()

    cv2.imshow("AI CCTV - YOLO Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()