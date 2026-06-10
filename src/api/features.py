from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from src.services import yolo_service

router = APIRouter()


class RuleModel(BaseModel):
    id: str
    name: Optional[str] = None
    feature: str
    description: Optional[str] = None
    enabled: bool = True


@router.get("/features")
def get_features():
    return yolo_service.get_features()


@router.get("/rules")
def get_rules():
    return yolo_service.get_rules()


@router.post("/rules")
def add_rule(rule: RuleModel):
    return yolo_service.add_rule(rule.dict())


@router.get("/compliance/{camera_id}")
def get_compliance(camera_id: int, helmet_compliance: bool = False, attendance: bool = False, object_detection: bool = True, face_recognition: bool = False):
    if attendance:
        face_recognition = True
    return yolo_service.evaluate_compliance(
        camera_id,
        helmet_compliance=helmet_compliance,
        attendance=attendance,
        object_detection=object_detection,
        face_recognition=face_recognition,
    )


@router.get("/attendance/records")
def attendance_records():
    return yolo_service.get_attendance_records()


@router.get("/attendance/{camera_id}")
def get_attendance(camera_id: int, mark: bool = False):
    # Running face recognition on a live frame; if mark=true, attendance is recorded.
    if mark:
        result = yolo_service.evaluate_compliance(camera_id, attendance=True, face_recognition=True)
        return {
            "camera_id": camera_id,
            "marked": result.get("attendance_marked", []),
            "recognized_faces": result.get("recognized_faces", []),
        }

    frame, error = yolo_service._capture_frame(camera_id)
    if error:
        raise HTTPException(status_code=500, detail=error)

    recognized_faces = yolo_service.recognize_faces(frame)
    return {
        "camera_id": camera_id,
        "recognized_faces": recognized_faces,
        "attendance_records": yolo_service.get_attendance_records(),
    }


@router.post("/attendance/clear")
def clear_attendance():
    return yolo_service.clear_attendance_records()
