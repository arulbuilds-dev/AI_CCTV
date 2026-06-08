from fastapi import APIRouter
from src.services import yolo_service

router = APIRouter()

@router.get("/detections")
def get_detections(camera_id: int = 0):
    return yolo_service.detect_from_webcam(camera_id)
