from fastapi import APIRouter
import cv2

router = APIRouter()

@router.get("/cameras")
def get_cameras():

    cameras = []

    for idx in range(5):

        cap = cv2.VideoCapture(idx)

        if cap.isOpened():

            cameras.append(
                {
                    "id": idx,
                    "name": f"Camera {idx}",
                    "status": "online",
                    "type": "USB"
                }
            )

        cap.release()

    return cameras