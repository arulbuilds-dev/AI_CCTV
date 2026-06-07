from fastapi import APIRouter
from src.services.yolo_service import YOLOService

router = APIRouter()

yolo_service = YOLOService()


@router.get("/counts")
def get_counts():
    return yolo_service.get_object_counts()