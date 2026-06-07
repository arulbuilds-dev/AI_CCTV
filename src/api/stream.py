# from fastapi import APIRouter
# from fastapi.responses import StreamingResponse
# from ultralytics import YOLO

# model = YOLO("yolo11n.pt")

# import cv2

# router = APIRouter()


# def generate_frames(camera_id):

#     camera = cv2.VideoCapture(camera_id)

#     while True:

#         success, frame = camera.read()
#         results = model(frame, verbose=False)

#         if not success:
#             break 
#         for box in results[0].boxes:

#             x1, y1, x2, y2 = map(int, box.xyxy[0])

#             confidence = float(box.conf[0])

#             class_id = int(box.cls[0])

#             label = model.names[class_id]

#             cv2.rectangle(
#                 frame,
#                 (x1, y1),
#                 (x2, y2),
#                 (0, 255, 0),
#                 2
#             )

#             cv2.putText(
#                 frame,
#                 f"{label} {confidence:.2f}",
#                 (x1, y1 - 10),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.5,
#                 (0, 255, 0),
#                 2
#             )

#         _, buffer = cv2.imencode(".jpg", frame)

#         frame_bytes = buffer.tobytes()

#         yield (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n\r\n"
#             + frame_bytes
#             + b"\r\n"
#         )


# # @router.get("/video")
# # def video_feed():

# #     return StreamingResponse(
# #         generate_frames(),
# #         media_type="multipart/x-mixed-replace; boundary=frame"
# #     )

# @router.get("/video/{camera_id}")
# def video_feed(camera_id: int):
#     camera = cv2.VideoCapture(camera_id)

#     while True:

#         success, frame = camera.read()

#         if not success:
#             break

#         _, buffer = cv2.imencode(".jpg", frame)

#         frame_bytes = buffer.tobytes()

#         yield (
#             b"--frame\r\n"
#             b"Content-Type: image/jpeg\r\n\r\n"
#             + frame_bytes
#             + b"\r\n"
#         )

#     camera.release() 

# @router.get("/video/{camera_id}")
# def video_feed(camera_id: int):

#     return StreamingResponse(
#         generate_frames(camera_id),
#         media_type="multipart/x-mixed-replace; boundary=frame"
#     )




from fastapi import APIRouter
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import cv2
import time
import asyncio
import requests



router = APIRouter()

print("Loading YOLO model...")
model = YOLO("yolo11n.pt")
print("YOLO model loaded.")


# def generate_frames(camera_id: int):

#     print(f"Opening Camera {camera_id}")

#     camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

#     if not camera.isOpened():
#         print(f"ERROR: Cannot open camera {camera_id}")
#         return

#     try:
#         while True:
#             print("Loop Start")

#             success, frame = camera.read()
#             print("Frame Read")

#             if not success or frame is None:
#                 print(f"Failed to read frame from camera {camera_id}")
#                 break

#             # YOLO Detection
#             results = model(frame, verbose=False)

#             for box in results[0].boxes:

#                 x1, y1, x2, y2 = map(int, box.xyxy[0])

#                 confidence = float(box.conf[0])

#                 class_id = int(box.cls[0])

#                 label = model.names[class_id]

#                 cv2.rectangle(
#                     frame,
#                     (x1, y1),
#                     (x2, y2),
#                     (0, 255, 0),
#                     2
#                 )

#                 cv2.putText(
#                     frame,
#                     f"{label} {confidence:.2f}",
#                     (x1, max(y1 - 10, 20)),
#                     cv2.FONT_HERSHEY_SIMPLEX,
#                     0.5,
#                     (0, 255, 0),
#                     2
#                 )

#             success, buffer = cv2.imencode(".jpg", frame)

#             if not success:
#                 print("Failed to encode frame")
#                 continue

#             frame_bytes = buffer.tobytes()
#             print("Before Yield")
#             yield (
#                 b"--frame\r\n"
#                 b"Content-Type: image/jpeg\r\n\r\n"
#                 + frame_bytes
#                 + b"\r\n"
#             )
#             time.sleep(0.03)
#             print("After Yield")

#     except Exception as e:
#         print(f"Video Stream Error: {e}")

#     finally:
#         print(f"Releasing Camera {camera_id}")
#         camera.release()


async def generate_frames(camera_id: int, request: Request):

    print(f"Opening Camera {camera_id}")

    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    try:

        while True:

            if await request.is_disconnected():
                print("CLIENT DISCONNECTED")
                break

            success, frame = camera.read()

            if not success:
                break

            _, buffer = cv2.imencode(".jpg", frame)

            frame_bytes = buffer.tobytes()

                        # YOLO Detection
            results = model(frame, verbose=False)

            for box in results[0].boxes:

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                confidence = float(box.conf[0])

                class_id = int(box.cls[0])

                label = model.names[class_id]

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"{label} {confidence:.2f}",
                    (x1, max(y1 - 10, 20)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
                print("Failed to encode frame")
                continue

            frame_bytes = buffer.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + frame_bytes
                + b"\r\n"
            )
            

            await asyncio.sleep(0.03)

    finally:

        print(f"Releasing Camera {camera_id}")

        camera.release()





# @router.get("/video/{camera_id}")
# def video_feed(camera_id: int):

#     return StreamingResponse(
#         generate_frames(camera_id),
#         media_type="multipart/x-mixed-replace; boundary=frame"
#     )

@router.get("/video/{camera_id}")
async def video_feed(
    camera_id: int,
    request: Request
):

    return StreamingResponse(
        generate_frames(camera_id, request),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )