import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image
import requests
from io import BytesIO
import uvicorn

app = FastAPI()

# 6 fərqli pulsuz karikatura modeli (Hugging Face)
MODELS = {
    "Pixar/Disney": "Ariel1997/pixar_cartoon_diffusion",
    "Anime": "Ariel1997/anime_gan_v2",
    "Simpsons": "Ariel1997/simpsons_cartoon",
    "Qələm karikaturası": "Ariel1997/pencil_sketch_cartoon",
    "Yağlı boya": "Ariel1997/oil_painting_cartoon",
    "Klassik karikatura": "Ariel1997/classic_cartoon"
}

def convert_to_cartoon(image_bytes, model_name):
    api_url = f"https://api-inference.huggingface.co/models/{model_name}"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', 'hf_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')}"}
    response = requests.post(api_url, headers=headers, data=image_bytes)
    return response.content

@app.get("/", response_class=HTMLResponse)
async def main():
    return """
    <html>
    <head><title>Karikatura Çevirici</title></head>
    <body style="font-family:Arial;text-align:center;margin-top:50px">
    <h1>Şəklini Karikaturaya Çevir (100% Pulsuz)</h1>
    <form action="/upload" enctype="multipart/form-data" method="post">
        <input name="file" type="file" accept="image/*" required><br><br>
        <button type="submit" style="padding:15px 30px;font-size:18px">Çevir!</button>
    </form>
    </body>
    </html>
    """

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    img = Image.open(BytesIO(contents))

    results = []
    for name, model in MODELS.items():
        try:
            cartoon_bytes = convert_to_cartoon(contents, model)
            cartoon_img = Image.open(BytesIO(cartoon_bytes))
            path = f"/tmp/{file.filename}_{name.replace('/', '')}.jpg"
            cartoon_img.save(path)
            results.append((name, path))
        except:
            pass  # bəzi modellər bəzən yüklənməyə bilər

    if not results:
        return {"error": "Model hazırda yüklənir, 1-2 dəqiqə sonra yenidən yoxla"}

    html = "<h2>Nəticələr:</h2><div style='display:flex;flex-wrap:wrap;justify-content:center'>"
    for title, path in results:
        html += f"<div style='margin:20px'><h3>{title}</h3><img src='/image/{os.path.basename(path)}' width='300'><br><a href='/image/{os.path.basename(path)}' download>Endir</a></div>"
    html += "</div><br><a href='/'>Yenidən çevir</a>"
    return HTMLResponse(html)

@app.get("/image/{filename}")
async def get_image(filename: str):
    return FileResponse(f"/tmp/{filename}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
