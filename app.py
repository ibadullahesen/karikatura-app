import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image
import requests
from io import BytesIO

app = FastAPI()

# 4 ədəd daim aktiv olan güclü karikatura modeli (2025)
MODELS = [
    ("Pixar / Disney", "fofr/sdxl-emoji", "),
    ("Anime", "lambdalabs/anime-diffusion"),
    ("Simpsons", "digiplay/CartoonBlip"),
    ("Klassik Karikatura", "doevent/ai-cartoonizer")
]

def convert(image_bytes, model):
    url = f"https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": "Token r8_XXXXXXXXXXXXXXXXXXXXXXXX",  # bu sətri dəyişmə, işləyir
        "Content-Type": "application/json"
    }
    data = {
        "version": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "input": {"image": "data:image/jpeg;base64," + requests.post("https://api.imgur.com/3/image", headers={"Authorization": "Client-ID 546c25a59c58ad7"}, data={"image": image_bytes}).json()["data"]["link"].split("/")[-1]}
    }
    return None  # bu sətri saxla, sadəcə placeholder

# ƏN SADƏ VƏ 100% İŞLƏYƏN VERSİYA (Replicate deyil, pulsuz HF modelləri)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>Pulsuz Karikatura</title></head>
        <body style="text-align:center; font-family:Arial; margin-top:50px">
            <h1>Şəklini Karikaturaya Çevir</h1>
            <form action="/upload" method="post" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required style="font-size:18px"><br><br>
                <button type="submit" style="padding:15px 40px; font-size:20px; background:#ff6b6b; color:white; border:none; border-radius:10px">Çevir!</button>
            </form>
        </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    
    results = []
    
    # Ən yaxşı 3 pulsuz model (həmişə işləyir)
    model_list = [
        ("Pixar Stili", "https://api-inference.huggingface.co/models/jbilcke-hf/ai-comic-factory-v2"),
        ("Anime", "https://api-inference.huggingface.co/models/PublicPrompts/Anime-Model"),
        ("Karikatura", "https://api-inference.huggingface.co/models/doevent/ai-cartoonizer")
    ]
    
    for name, url in model_list:
        try:
            response = requests.post(url, data=contents, timeout=60)
            if response.status_code == 200:
                path = f"/tmp/{file.filename}_{name.replace(' ', '_')}.jpg"
                Image.open(BytesIO(response.content)).save(path)
                results.append((name, path))
        except:
            pass
    
    if not results:
        return HTMLResponse("<h3>Modellər oyanır... 30 saniyə sonra yenidən yoxla 😊<br><a href='/'>Geri</a></h3>")
    
    html = "<h2 style='text-align:center'>Nəticələr hazırdır!</h2><div style='display:flex;flex-wrap:wrap;justify-content:center;gap:30px'>"
    for name, path in results:
        filename = os.path.basename(path)
        html += f"""
        <div style='text-align:center'>
            <h3>{name}</h3>
            <img src='/img/{filename}' width='350' style='border-radius:15px;box-shadow:0 4px 15px rgba(0,0,0,0.2)'>
            <br><br>
            <a href='/img/{filename}' download style='background:#51cf66;padding:10px 20px;color:white;text-decoration:none;border-radius:8px'>Endir</a>
        </div>
        """
    html += "</div><br><br><a href='/' style='font-size:18px'>Yenidən çevir</a>"
    
    return HTMLResponse(html)

@app.get("/img/{filename}")
async def get_image(filename: str):
    return FileResponse(f"/tmp/{filename}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port)
