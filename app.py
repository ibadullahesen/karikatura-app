from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import uuid
import io

app = FastAPI()

# Şəkillər üçün qovluq
os.makedirs("/tmp/cartoon_images", exist_ok=True)

# 🎨 KARİKATURA MODELLƏRİ
MODELS = [
    {"name": "🎭 Karikatura", "description": "Canlı rənglər", "type": "cartoon"},
    {"name": "✏️ Qələm", "description": "Qara-ağ çəkiliş", "type": "pencil"},
    {"name": "🌟 Anime", "description": "Parlaq rənglər", "type": "anime"},
    {"name": "🎨 Komik", "description": "Komik kitab stili", "type": "comic"}
]

def apply_cartoon_effect(image):
    """Karikatura effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if max(img.size) > 800:
            img.thumbnail((800, 800))
        
        # Kənarları tap
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Brightness(edges).enhance(2.0)
        
        # Rəngləri canlandır
        enhanced = ImageEnhance.Color(img).enhance(1.6)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        
        # Rəng sayını azalt
        quantized = enhanced.quantize(colors=16)
        quantized = quantized.convert('RGB')
        
        # Kənarları əlavə et
        final = Image.blend(quantized, edges.convert('RGB'), 0.08)
        return final
        
    except Exception as e:
        print(f"Karikatura xətası: {e}")
        return image

def apply_pencil_sketch(image):
    """Qələm çəkilişi"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800))
        
        gray = img.convert('L')
        inverted = ImageOps.invert(gray)
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=2))
        pencil = Image.blend(gray, blurred, 0.75)
        pencil = ImageEnhance.Contrast(pencil).enhance(2.0)
        
        return pencil.convert('RGB')
        
    except Exception as e:
        print(f"Qələm xətası: {e}")
        return image

def apply_anime_effect(image):
    """Anime effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800))
        
        enhanced = ImageEnhance.Color(img).enhance(1.8)
        enhanced = ImageEnhance.Brightness(enhanced).enhance(1.1)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)
        
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        quantized = sharpened.quantize(colors=32)
        return quantized.convert('RGB')
        
    except Exception as e:
        print(f"Anime xətası: {e}")
        return image

def apply_comic_effect(image):
    """Komik effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800))
        
        quantized = img.quantize(colors=12)
        quantized = quantized.convert('RGB')
        
        enhanced = ImageEnhance.Contrast(quantized).enhance(1.8)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(3.0)
        
        return enhanced
        
    except Exception as e:
        print(f"Komik xətası: {e}")
        return image

@app.get("/", response_class=HTMLResponse)
async def ana_səhifə():
    return """
    <!DOCTYPE html>
    <html lang="az">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Karikatura Çevirici</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 30px;
                border-radius: 15px;
            }
            h1 {
                color: #ffd700;
                margin-bottom: 10px;
            }
            .upload-area {
                border: 2px dashed #ffd700;
                border-radius: 10px;
                padding: 30px;
                margin: 20px 0;
                background: rgba(255, 255, 255, 0.1);
                cursor: pointer;
            }
            .file-input {
                display: none;
            }
            .upload-btn {
                background: #ff6b6b;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 1.1em;
                border-radius: 25px;
                cursor: pointer;
                margin-top: 10px;
            }
            .upload-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
            }
            .loading {
                display: none;
                margin: 20px 0;
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 3px solid #ffd700;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Karikatura Çevirici</h1>
            <p>Şəklini karikaturaya çevir!</p>
            
            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <h3>📁 Şəkil Seç</h3>
                    <p>Faylı buraya klikləyin</p>
                </div>
                <div id="fileName" style="margin: 10px 0; color: #ffd700;"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Şəkil işlənir...</p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    Çevir
                </button>
            </form>
        </div>

        <script>
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const fileName = document.getElementById('fileName');
                if (this.files.length > 0) {
                    fileName.textContent = 'Seçildi: ' + this.files[0].name;
                }
            });

            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileInput');
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                
                if (!fileInput.files.length) {
                    alert('Şəkil seçin!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                submitBtn.disabled = true;
                loading.style.display = 'block';

                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });

                    if (response.ok) {
                        const html = await response.text();
                        document.body.innerHTML = html;
                    } else {
                        throw new Error('Xəta baş verdi');
                    }
                } catch (error) {
                    alert(error.message);
                } finally {
                    submitBtn.disabled = false;
                    loading.style.display = 'none';
                }
            });
        </script>
    </body>
    </html>
    """

@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Yalnız şəkil faylları")

        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Düzgün olmayan şəkil")

        image = Image.open(io.BytesIO(contents))
        
        results = []
        unique_id = str(uuid.uuid4())[:8]

        for model in MODELS:
            try:
                if model['type'] == "cartoon":
                    result_image = apply_cartoon_effect(image)
                elif model['type'] == "pencil":
                    result_image = apply_pencil_sketch(image)
                elif model['type'] == "anime":
                    result_image = apply_anime_effect(image)
                elif model['type'] == "comic":
                    result_image = apply_comic_effect(image)
                else:
                    result_image = apply_cartoon_effect(image)
                
                filename = f"cartoon_{unique_id}_{model['type']}.jpg"
                filepath = f"/tmp/cartoon_images/{filename}"
                
                result_image.save(filepath, "JPEG", quality=85)
                results.append({
                    'name': model['name'],
                    'description': model['description'],
                    'filename': filename
                })
                
            except Exception as e:
                print(f"Xəta: {model['name']}: {e}")
                continue

        if not results:
            return HTMLResponse("""
            <html>
            <body style="font-family: Arial; text-align: center; margin-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                <div style="background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #ffd700;">Xəta</h1>
                    <p>Yenidən cəhd edin.</p>
                    <a href="/" style="background: #ff6b6b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Yenidən cəhd et</a>
                </div>
            </body>
            </html>
            """)

        html = """
        <!DOCTYPE html>
        <html lang="az">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nəticələr</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                }
                .container {
                    max-width: 1000px;
                    margin: 0 auto;
                }
                h1 {
                    text-align: center;
                    color: #ffd700;
                }
                .results {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 30px 0;
                }
                .result {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 10px;
                    text-align: center;
                }
                .result img {
                    width: 100%;
                    max-width: 200px;
                    height: 200px;
                    object-fit: cover;
                    border-radius: 5px;
                }
                .download {
                    background: #27ae60;
                    color: white;
                    padding: 8px 15px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                    margin-top: 10px;
                }
                .back {
                    background: #3498db;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    display: inline-block;
                }
                .center {
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Nəticələr Hazırdır!</h1>
                <div class="results">
        """

        for result in results:
            html += f"""
                    <div class="result">
                        <h3>{result['name']}</h3>
                        <p>{result['description']}</p>
                        <img src="/img/{result['filename']}" alt="{result['name']}">
                        <br>
                        <a href="/img/{result['filename']}" download="{result['filename']}" class="download">Endir</a>
                    </div>
            """

        html += """
                </div>
                <div class="center">
                    <a href="/" class="back">Yenidən Çevir</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(html)

    except Exception as e:
        print(f"Ümumi xəta: {e}")
        return HTMLResponse("""
        <html>
        <body style="font-family: Arial; text-align: center; margin-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #ffd700;">Xəta</h1>
                <p>Yenidən cəhd edin.</p>
                <a href="/" style="background: #ff6b6b; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Yenidən cəhd et</a>
            </div>
        </body>
        </html>
        """)

@app.get("/img/{filename}")
async def img(filename: str):
    filepath = f"/tmp/cartoon_images/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Şəkil tapılmadı")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
