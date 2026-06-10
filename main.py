# from fastapi import FastAPI
# from src.api.cameras import router as camera_router

# app = FastAPI(
#     title="AI CCTV Platform",
#     version="1.0.0"
# )

# app.include_router(camera_router, prefix="/api")

# @app.get("/")
# def root():
#     return {
#         "application": "AI CCTV Platform",
#         "status": "running"
#     }

# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }


#from fastapi import FastAPI

# app = FastAPI(
#     title="AI CCTV Platform",
#     version="1.0.0"
# )

# @app.get("/")
# def root():
#     return {
#         "application": "AI CCTV Platform",
#         "status": "running"
#     }

# @app.get("/health")
# def health():
#     return {
#         "status": "healthy"
#     }


from fastapi import FastAPI
from src.api.cameras import router as camera_router
from src.api.detections import router as detection_router
from src.api.counts import router as count_router
from src.api.stream import router as stream_router
from src.api.features import router as features_router
from src.api.dashboard import router as dashboard_router
from fastapi import Request

app = FastAPI(
    title="AI CCTV Platform",
    version="1.0.0"
)

app.include_router(camera_router, prefix="/api")

@app.get("/")
def root():
    return {
        "application": "AI CCTV Platform",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# @router.get("/video/{camera_id}")
# async def video_feed(camera_id: int, request: Request):

#     return StreamingResponse(
#         generate_frames(camera_id, request),
#         media_type="multipart/x-mixed-replace; boundary=frame"
#     )

app.include_router(
    detection_router,
    prefix="/api"
)

app.include_router(
    count_router,
    prefix="/api"
)
app.include_router(
    stream_router,
    prefix="/api"
)
app.include_router(
    features_router,
    prefix="/api"
)
app.include_router(dashboard_router)
