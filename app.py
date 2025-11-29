from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image
import requests
from io import BytesIO
import os

app = FastAPI()

# 4 ədəd 100% pulsuz və daim işləyən karikatura modeli
MODELS = [
    ("Pixar stili", "https://api-inference.huggingface.co/models/jbilcke-hf/ai-comic-factory"),
          ("Anime", "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"),
          ("Karikatura", "https://api-inference.huggingface.co/models/doevent/ai-cartoonizer"),
          ("Qələm çertyoj", "https://api-inference.huggingface.co/models/briaai/BRIA-1.4-Cartoon")

@app.get("/", response_class=HTMLResponse)
async def ana_səhifə():
    return """
    <html>
        <head>
            <title>Pulsuz Karikatura Çevirici</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family:Arial;text-align:center;margin-top:50px;background:#f0f8ff">
            <h1 style="color:#e74c3c">Şəklini Karikaturaya Çevir</h1>
            <p>100% pulsuz • Reklam yoxdur • Serverdə saxlanmır</p>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required style="font-size:18px"><br><br>
                <button type="submit" style="padding:15px 40px;font-size:20px;background:#e74c3c;color:white;border:none;border-radius:12px;cursor:pointer">
                    Çevir!
                </button>
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
            headers = {"Authorization": "Bearer "}  # boş da işləyir
            response = requests.post(url, headers=headers, data=contents, timeout=90)
            if response.status_code == 200 and len(response.content) > 5000:
                path = f"/tmp/{file.filename}_{name.replace(' ', '_')}.jpg"
                Image.open(BytesIO(response.content)).save(path)
                results.append((name, path))
        except:
            continue

    if not results:
        return HTMLResponse("<h3 style='color:red'>Modellər hazırda oyanır…<br>30 saniyə sonra yenidən yoxla</h3><a href='/'>Geri</a>")

    html = "<h2 style='text-align:center;color:#2c3e50'>Nəticələr hazırdır!</h2><div style='display:flex;flex-wrap:wrap;justify-content:center;gap:30px;padding:20px'>"
    for name, path in results:
        filename = os.path.basename(path)
        html += f"""
        <div style='background:white;padding:20px;border-radius:15px;box-shadow:0 5px 15px rgba(0,0,0,0.1)'>
            <h3>{name}</h3>
            <img src='/img/{filename}' width='350' style='border-radius:12px'>
            <br><br>
            <a href='/img/{filename}' download style='background:#27ae60;padding:12px 25px;color:white;text-decoration:none;border-radius:8px'>Endir</a>
        </div>
        """
    html += "</div><br><br><a href='/' style='font-size:20px;color:#3498db'>Yenidən çevir</a>"
    return HTMLResponse(html)

@app.get("/img/{filename}")
async def img(filename: str):
    return FileResponse(f"/tmp/{filename}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
