from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    html = """
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8" />
        <title>AI CCTV Dashboard</title>
        <style>body{font-family:Arial,Helvetica,sans-serif;margin:16px;} .container{display:flex;gap:16px;} .panel{flex:1}</style>
      </head>
      <body>
        <h1>AI CCTV Dashboard</h1>
        <p>
          Live stream (MJPEG):
        </p>
        <div class="container">
          <div class="panel">
            <img src="/api/video/0" alt="Live Stream" style="width:100%;max-width:800px;border:1px solid #ccc;" />
          </div>
          <div class="panel">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="/docs" target="_blank">Swagger UI (/docs)</a></li>
              <li><a href="/api/cameras" target="_blank">/api/cameras</a></li>
              <li><a href="/api/detections" target="_blank">/api/detections</a></li>
              <li><a href="/api/counts" target="_blank">/api/counts</a></li>
            </ul>
            <p>Camera ID for the embedded stream: <strong>0</strong></p>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
