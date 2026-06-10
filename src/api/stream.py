from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, Response
import cv2
import asyncio
from src.services import yolo_service

router = APIRouter()


async def generate_frames(camera_id: int, request: Request, object_detection: bool = False, face_recognition: bool = False, helmet_detection: bool = False, annotate: bool = True):
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    try:
        while True:
            if await request.is_disconnected():
                break

            success, frame = camera.read()
            if not success or frame is None:
                break

            # Apply requested AI features
            frame = yolo_service.annotate_frame(
                frame,
                object_detection=object_detection,
                face_recognition=face_recognition,
                helmet_detection=helmet_detection,
                annotate=annotate,
            )
            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
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
        camera.release()


@router.get("/video/{camera_id}")
async def video_feed(camera_id: int, request: Request, object_detection: bool = False, face_recognition: bool = False, helmet_detection: bool = False, annotate: bool = True):
    return StreamingResponse(
        generate_frames(
            camera_id,
            request,
            object_detection=object_detection,
            face_recognition=face_recognition,
            helmet_detection=helmet_detection,
            annotate=annotate,
        ),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.get("/snapshot/{camera_id}")
async def snapshot(camera_id: int, object_detection: bool = False, face_recognition: bool = False, helmet_detection: bool = False, annotate: bool = True):
    # Capture a single frame and return as JPEG
    frame, error = yolo_service._capture_frame(camera_id)

    if error:
        return Response(content=str(error), media_type="text/plain", status_code=500)

    frame = yolo_service.annotate_frame(
        frame,
        object_detection=object_detection,
        face_recognition=face_recognition,
        helmet_detection=helmet_detection,
        annotate=annotate,
    )
    success, buffer = cv2.imencode('.jpg', frame)
    if not success:
        return Response(content='Failed to encode image', media_type='text/plain', status_code=500)

    return Response(content=buffer.tobytes(), media_type='image/jpeg')
