from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image
import requests
from io import BytesIO
import os

app = FastAPI()

# 3 ədəd 100% pulsuz və daim işləyən karikatura modeli
MODELS = [
    ("Pixar / Disney", "https://api-inference.huggingface.co/models/jbilcke-hf/ai-comic-factory"),
    ("Anime", "https://api-inference.huggingface.co/models/HumanityScatterbrain/anime-portrait-diffusion"),
    ("Klassik Karikatura", "https://api-inference.huggingface.co/models/doevent/ai-cartoonizer")
]

@app.get("/", response_class=HTMLResponse)
async def ana_sehife():
    return """
    <html>
      <head>
        <title>Pulsuz Karikatura</title>
        <meta charset="utf-8">
        <style>
          body {font-family:Arial;text-align:center;background:#f8f9fa;padding:50px;}
          button {padding:15px 40px;font-size:22px;background:#ff4757;color:white;border:none;border-radius:12px;cursor:pointer;}
        </style>
      </head>
      <body>
        <h1>Şəklini Karikaturaya Çevir</h1>
        <p>100% pulsuz • Reklam yoxdur</p>
        <form action="/upload" method="post enctype="multipart/form-data">
          <input type="file" name="file" accept="image/*" required style="font-size:18px"><br><br>
          <button type="submit">Çevir!</button>
        </form>
      </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    results = []

    for name, url in MODELS:
        try:
            r = requests.post(url, data=contents, timeout=90)
            if r.status_code == 200 and len(r.content) > 3000:
                path = f"/tmp/{file.filename}_{name.replace(' ', '_').replace('/', '')}.jpg"
                Image.open(BytesIO(r.content)).save(path)
                results.append((name, path))
        except:
            continue

    if not results:
        return "<h3>Modellər oyanır... 30 saniyə sonra yenidən sına</h3><a href='/'>Geri</a>"

    html = "<h2>Nəticələr:</h2><div style='display:flex;flex-wrap:wrap;justify-content:center;gap:30px'>"
    for name, path in results:
        fn = os.path.basename(path)
        html += f"""
        <div style='text-align:center'>
          <h3>{name}</h3>
          <img src='/img/{fn}' width='400' style='border-radius:15px'>
          <br><br>
          <a href='/img/{fn}' download style='background:#2ed573;padding:12px 25px;color:white;text-decoration:none;border-radius:8px'>Endir</a>
        </div>
        """
    html += "</div><br><a href='/'>Yenidən çevir</a>"
    return HTMLResponse(html)

@app.get("/img/{filename}")
async def img(filename: str):
    return FileResponse(f"/tmp/{filename}")

# Render üçün düzgün port
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
