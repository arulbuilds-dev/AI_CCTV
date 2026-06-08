from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import cv2
import asyncio
from src.services import yolo_service

router = APIRouter()

async def generate_frames(camera_id: int, request: Request):
    camera = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)

    try:
        while True:
            if await request.is_disconnected():
                break

            success, frame = camera.read()
            if not success or frame is None:
                break

            frame = yolo_service.annotate_frame(frame)
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
async def video_feed(camera_id: int, request: Request):
    return StreamingResponse(
        generate_frames(camera_id, request),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
