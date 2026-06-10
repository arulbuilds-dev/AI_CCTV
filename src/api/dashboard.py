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
        <div style="margin-bottom:12px">
          <label for="cameraSelect">Camera:</label>
          <select id="cameraSelect"></select>
          &nbsp;&nbsp;
          <label><input type="checkbox" id="objectDet" checked /> Object Detection</label>
          &nbsp;&nbsp;
          <label><input type="checkbox" id="faceRec" /> Face Recognition</label>
          &nbsp;&nbsp;
          <label><input type="checkbox" id="helmetDet" /> Helmet Compliance</label>
          &nbsp;&nbsp;
          <label><input type="checkbox" id="attendanceRule" /> Attendance</label>
          &nbsp;&nbsp;
          <button id="applyBtn">Apply</button>
          &nbsp;&nbsp;
          <button id="startStopBtn">Stop</button>
          &nbsp;&nbsp;
          <button id="snapshotBtn">Snapshot</button>
          &nbsp;&nbsp;
          <button id="checkRulesBtn">Check Rules</button>
        </div>
        <div class="container">
          <div class="panel">
            <img id="streamImg" src="/api/video/0" alt="Live Stream" style="width:100%;max-width:800px;border:1px solid #ccc;" />
          </div>
          <div class="panel">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="/docs" target="_blank">Swagger UI (/docs)</a></li>
              <li><a href="/api/cameras" target="_blank">/api/cameras</a></li>
              <li><a href="/api/detections" target="_blank">/api/detections</a></li>
              <li><a href="/api/counts" target="_blank">/api/counts</a></li>
              <li><a href="/api/features" target="_blank">/api/features</a></li>
              <li><a href="/api/rules" target="_blank">/api/rules</a></li>
              <li><a href="/api/attendance/records" target="_blank">/api/attendance/records</a></li>
            </ul>
            <p id="currentConfig">Camera ID: <strong>0</strong></p>
            <div id="ruleResults" style="margin-top:16px;padding:10px;border:1px solid #ddd;background:#f9f9f9;"></div>
            <h4>Snapshot</h4>
            <img id="snapshotImg" src="" alt="Snapshot" style="width:100%;max-width:300px;border:1px solid #ccc;display:block;margin-top:8px;" />
          </div>
        </div>

        <script>
          async function loadCameras(){
            try{
              const res = await fetch('/api/cameras');
              const cams = await res.json();
              const sel = document.getElementById('cameraSelect');
              sel.innerHTML = '';
              if(!cams || cams.length === 0){
                const opt = document.createElement('option');
                opt.value = '0';
                opt.text = 'Camera 0 (default)';
                sel.appendChild(opt);
                return;
              }
              cams.forEach(c=>{
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.text = c.name || ('Camera ' + c.id);
                sel.appendChild(opt);
              });
            }catch(e){
              console.warn('Failed to load cameras', e);
            }
          }

          function buildStreamUrl(){
            const cam = document.getElementById('cameraSelect').value || 0;
            const obj = document.getElementById('objectDet').checked ? 'true' : 'false';
            const face = document.getElementById('faceRec').checked ? 'true' : 'false';
            const helmet = document.getElementById('helmetDet').checked ? 'true' : 'false';
            const ts = Date.now();
            return `/api/video/${cam}?object_detection=${obj}&face_recognition=${face}&helmet_detection=${helmet}&annotate=true&ts=${ts}`;
          }

          function buildComplianceUrl(){
            const cam = document.getElementById('cameraSelect').value || 0;
            const helmet = document.getElementById('helmetDet').checked ? 'true' : 'false';
            const attendance = document.getElementById('attendanceRule').checked ? 'true' : 'false';
            const face = document.getElementById('faceRec').checked || document.getElementById('attendanceRule').checked ? 'true' : 'false';
            return `/api/compliance/${cam}?helmet_compliance=${helmet}&attendance=${attendance}&object_detection=true&face_recognition=${face}`;
          }

          const applyBtn = document.getElementById('applyBtn');
          const startStopBtn = document.getElementById('startStopBtn');
          const snapshotBtn = document.getElementById('snapshotBtn');
          const checkRulesBtn = document.getElementById('checkRulesBtn');
          let streaming = true;

          applyBtn.addEventListener('click', ()=>{
            const url = buildStreamUrl();
            const img = document.getElementById('streamImg');
            img.src = '';
            img.src = url;
            document.getElementById('currentConfig').innerHTML = `Camera ID: <strong>${document.getElementById('cameraSelect').value}</strong><br>Object Detection: <strong>${document.getElementById('objectDet').checked}</strong><br>Face Recognition: <strong>${document.getElementById('faceRec').checked}</strong><br>Helmet Compliance: <strong>${document.getElementById('helmetDet').checked}</strong><br>Attendance: <strong>${document.getElementById('attendanceRule').checked}</strong>`;
            streaming = true;
            startStopBtn.textContent = 'Stop';
          });

          startStopBtn.addEventListener('click', ()=>{
            if(streaming){
              document.getElementById('streamImg').src = '';
              startStopBtn.textContent = 'Start';
            } else {
              document.getElementById('streamImg').src = buildStreamUrl();
              startStopBtn.textContent = 'Stop';
            }
            streaming = !streaming;
          });

          snapshotBtn.addEventListener('click', async ()=>{
            const cam = document.getElementById('cameraSelect').value || 0;
            const obj = document.getElementById('objectDet').checked ? 'true' : 'false';
            const face = document.getElementById('faceRec').checked ? 'true' : 'false';
            const helmet = document.getElementById('helmetDet').checked ? 'true' : 'false';
            const ts = Date.now();
            const url = `/api/snapshot/${cam}?object_detection=${obj}&face_recognition=${face}&helmet_detection=${helmet}&annotate=true&ts=${ts}`;
            try{
              const res = await fetch(url);
              if(!res.ok) throw new Error('Snapshot failed');
              const blob = await res.blob();
              const imgUrl = URL.createObjectURL(blob);
              const snap = document.getElementById('snapshotImg');
              snap.src = imgUrl;
            }catch(e){
              alert('Snapshot failed: ' + e.message);
            }
          });

          checkRulesBtn.addEventListener('click', async ()=>{
            const url = buildComplianceUrl();
            const ruleArea = document.getElementById('ruleResults');
            ruleArea.textContent = 'Checking rules...';
            try{
              const res = await fetch(url);
              if(!res.ok) throw new Error('Rules check failed');
              const data = await res.json();
              ruleArea.innerHTML = `<pre style="white-space:pre-wrap;">${JSON.stringify(data, null, 2)}</pre>`;
            }catch(e){
              ruleArea.textContent = 'Error: ' + e.message;
            }
          });

          // initialize
          loadCameras().then(()=>{
            document.getElementById('cameraSelect').value = '0';
            applyBtn.click();
          });
        </script>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
