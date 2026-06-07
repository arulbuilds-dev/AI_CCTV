import cv2

camera_id = 0
camera_id = 1

cap = cv2.VideoCapture(camera_id)

while True:

    ret, frame = cap.read()

    if not ret:
        print("Failed to read frame")
        break

    cv2.imshow(f"Camera {camera_id}", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()