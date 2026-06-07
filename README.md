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

Run the API server
------------------

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Notes
-----
- The app currently uses `yolo11n.pt` for inference and expects this model file to be present in the repo root.
- `requirements.txt` has been updated to include the FastAPI stack and Ultralytics.
- The current detection routes use the system webcam and may need refactoring for multi-camera or dashboard use.
