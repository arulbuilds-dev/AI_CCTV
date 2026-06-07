# from fastapi import APIRouter
# from src.services.yolo_service import YOLOService

# router = APIRouter()

# yolo_service = YOLOService()

# @router.get("/detections")
# def get_detections():

#     result = yolo_service.detect(...)

#     return result

from fastapi import APIRouter
from src.services.yolo_service import YOLOService

router = APIRouter()

yolo_service = YOLOService()


@router.get("/detections")
def get_detections():
    return yolo_service.detect_from_webcam()