AI_CCTV
========

Project: AI CCTV with Python APIs and dashboard.

Quick start
-----------

1. Create a Python virtual environment and install dependencies:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

2. Run tests or examples (inspect `src/` and top-level scripts):

```bash
python gpu_test.py
python main.py
```

Repository
----------

This repo contains models and large files under `data/`, `models/`, and `outputs/` which are ignored by `.gitignore`.

Project structure
-----------------
- `main.py` — FastAPI app entrypoint, registers API routers.
- `src/api/cameras.py` — discovers local USB cameras using OpenCV.
- `src/api/detections.py` — runs YOLO detection on the webcam and returns raw detection results.
- `src/api/counts.py` — returns aggregated object counts from YOLO detections.
- `src/api/stream.py` — MJPEG video stream endpoint with YOLO overlay.
- `src/services/yolo_service.py` — loads `yolo11n.pt` and performs frame detection.
- `gpu_test.py`, `webcam_test.py`, `pytourch.py`, `pytourch1.py` — development/test scripts.

API endpoints
-------------
- `GET /` — health/status check.
- `GET /health` — health endpoint.
- `GET /api/cameras` — list available local camera devices.
- `GET /api/detections` — detect objects on webcam frame.
- `GET /api/counts` — count detected objects by label.
- `GET /api/video/{camera_id}` — stream MJPEG frames from camera with YOLO overlay.
- `GET /api/features` — list supported AI features such as object detection, face recognition, helmet compliance.
- `GET /api/rules` — list active monitoring rules.
- `GET /api/compliance/{camera_id}` — evaluate helmet compliance and/or attendance rules on one camera frame.
- `GET /api/attendance/{camera_id}` — perform face recognition and return recognized faces.
- `GET /api/attendance/records` — return stored attendance records.

Run the API server
------------------

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Dashboard and rules
-------------------
- Open `http://127.0.0.1:8000/dashboard` to use the live stream, snapshot, helmet compliance, and attendance controls.
- Use the `Check Rules` button to evaluate helmet compliance and face recognition attendance for the selected camera.
- For rule API access, try:
  - `GET /api/compliance/0?helmet_compliance=true&attendance=true`
  - `GET /api/attendance/0?mark=true`

Notes
-----
- The app currently uses `yolo11n.pt` for inference and expects this model file to be present in the repo root.
- `requirements.txt` has been updated to include the FastAPI stack, Ultralytics, and OpenCV contrib for face recognition support.
- For attendance, add labeled face images under `data/faces/<person_name>/` and restart the server so the recognizer loads the known identities.
- The current detection routes use the system webcam and may need refactoring for multi-camera or dashboard use.
