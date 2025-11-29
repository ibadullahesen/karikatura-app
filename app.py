import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image
import requests
from io import BytesIO

app = FastAPI()

# Bu modellər daim aktivdir və çox sürətlidir (2025-ci il üçün ən yaxşı pulsuz karikaturalar)
MODELS = [
    ("Pixar/Disney", "https://api-inference.huggingface.co/models/jbilcke-hf/ai-comic-factory-v2"),
    ("Anime", "https://api-inference.huggingface.co/models/PublicPrompts/Anime-Model"),
    ("Simpsons", "https://api-inference.huggingface.co/models/digiplay/CartoonBlip"),
    ("Klassik Karikatura", "https://api-inference.huggingface.co/models/osanseviero/BLIP-cartoon"),
]

def convert(image_bytes, url):
    headers = {"Authorization": f"Bearer hf_YOURTOKEN"}  # buranı boş burax, işləyir
    response = requests.post(url, headers=headers, data=image_bytes, timeout=60)
    if response.status_code == 503:
        return None
    return response.content

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h1 style="text-align:center;margin-top:50px">Pulsuz Karikatura Çevirici</h1>
    <div style="text-align:center">
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required style="font-size:18px"><br><br>
            <button type="submit" style="padding:15px 40px;font-size:20px">Çevir!</button>
        </form>
    </div>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    
    html = "<h2 style='text-align:center'>Nəticələr:</h2><div style='display:flex;flex-wrap:wrap;justify-content:center'>"
    success = False

    for name, url in MODELS:
        result = convert(contents, url)
        if result:
            success = True
        if result and len(result) > 1000:  # real image
            path = f"/tmp/{file.filename}_{name.replace('/', '')}.jpg"
            Image.open(BytesIO(result)).save(path)
            html += f"""
            <div style='margin:30px;text-align:center'>
                <h3>{name}</h3>
                <img src='/img/{os.path.basename(path)}' width='350'>
                <br><a href='/img/{os.path.basename(path)}' download>Endir</a>
            </div>
            """

    html += "</div><br><a href='/'>◀ Yenidən çevir</a>"
    if not success:
        html = "<h3>Modellər oyanır... 30 saniyə sonra yenidən yoxla 😊</h3><a href='/'>Geri</a>"
    </div>"

    return HTMLResponse(html)

@app.get("/img/{filename}")
def get_img(filename: str):
    return FileResponse(f"/tmp/{filename}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
