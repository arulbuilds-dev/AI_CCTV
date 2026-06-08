from fastapi import APIRouter
from src.services import yolo_service

router = APIRouter()

@router.get("/counts")
def get_counts(camera_id: int = 0):
    return yolo_service.get_object_counts(camera_id)
