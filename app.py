from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
import requests
from io import BytesIO
import os
import uuid
import time

app = FastAPI()

# Static fayllar üçün qovluq yaradın
os.makedirs("static", exist_ok=True)
os.makedirs("/tmp/cartoon_images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Daha etibarlı karikatura modelləri
MODELS = [
    ("Karikatura stili", "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion"),
    ("Anime stili", "https://api-inference.huggingface.co/models/22h/vintage-anime-diffusion"),
    ("Rəssam çəkilişi", "https://api-inference.huggingface.co/models/wavymulder/Analog-Diffusion"),
    ("Piksar stili", "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion")
]

@app.get("/", response_class=HTMLResponse)
async def ana_səhifə():
    return """
    <!DOCTYPE html>
    <html lang="az">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Pulsuz Karikatura Çevirici</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                text-align: center;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                color: #ffd700;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
            .features {
                display: flex;
                justify-content: center;
                gap: 20px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .feature {
                background: rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 0.9em;
            }
            .upload-area {
                border: 3px dashed #ffd700;
                border-radius: 15px;
                padding: 40px;
                margin: 30px 0;
                background: rgba(255, 255, 255, 0.1);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: scale(1.02);
            }
            .file-input {
                display: none;
            }
            .upload-btn {
                background: #ff6b6b;
                color: white;
                border: none;
                padding: 15px 40px;
                font-size: 1.2em;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
            }
            .upload-btn:hover {
                background: #ff5252;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
            }
            .upload-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                display: none;
                margin: 20px 0;
            }
            .spinner {
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 4px solid #ffd700;
                width: 40px;
                height: 40px;
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
            <h1>🎨 Şəklini Karikaturaya Çevir</h1>
            <p style="font-size: 1.2em; margin-bottom: 30px;">AI ilə şəkillərinizi unikal karikaturalara çevirin</p>
            
            <div class="features">
                <div class="feature">✅ 100% Pulsuz</div>
                <div class="feature">🚀 Reklam yoxdur</div>
                <div class="feature">🔒 Şəkillər saxlanmır</div>
                <div class="feature">⚡ 4 fərqli stil</div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <h3>📁 Şəkil seçin</h3>
                    <p>Faylı buraya sürükləyin və ya klikləyin</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">(JPG, PNG, WEBP - Maksimum 5MB)</p>
                </div>
                <div id="fileName" style="margin: 10px 0;"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Şəkil karikaturaya çevrilir... Bu, bir neçə dəqiqə çəkə bilər</p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    🎨 KARİKATURAYA ÇEVİR!
                </button>
            </form>
        </div>

        <script>
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const fileName = document.getElementById('fileName');
                if (this.files.length > 0) {
                    fileName.textContent = 'Seçilmiş fayl: ' + this.files[0].name;
                } else {
                    fileName.textContent = '';
                }
            });

            document.getElementById('uploadForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const fileInput = document.getElementById('fileInput');
                const submitBtn = document.getElementById('submitBtn');
                const loading = document.getElementById('loading');
                
                if (!fileInput.files.length) {
                    alert('Zəhmət olmasa şəkil seçin!');
                    return;
                }

                // Fayl ölçüsünü yoxla (5MB)
                if (fileInput.files[0].size > 5 * 1024 * 1024) {
                    alert('Fayl ölçüsü 5MB-dan çox olmamalıdır!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                // Loading rejimini aktiv et
                submitBtn.disabled = true;
                submitBtn.textContent = 'Çevrilir...';
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
                        throw new Error('Server xətası');
                    }
                } catch (error) {
                    alert('Xəta baş verdi: ' + error.message + '. Zəhmət olmasa yenidən cəhd edin.');
                    console.error('Error:', error);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🎨 KARİKATURAYA ÇEVİR!';
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
        # Fayl tipini yoxla
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Yalnız şəkil faylları qəbul edilir")

        contents = await file.read()
        
        # Şəkli yoxla
        try:
            image = Image.open(BytesIO(contents))
            image.verify()  # Şəklin düzgün olub olmadığını yoxla
        except Exception:
            raise HTTPException(status_code=400, detail="Düzgün olmayan şəkil faylı")

        # Şəkli yenidən aç və ölçüsünü tənzimlə
        image = Image.open(BytesIO(contents))
        if image.size[0] > 1024 or image.size[1] > 1024:
            image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        
        # Şəkli optimallaşdır
        output = BytesIO()
        image.save(output, format='JPEG', quality=85, optimize=True)
        optimized_contents = output.getvalue()

        results = []
        unique_id = str(uuid.uuid4())[:8]

        for name, url in MODELS:
            try:
                print(f"Model işləyir: {name}")
                
                # API sorğusu üçün headers
                headers = {
                    "Authorization": "Bearer ",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                
                # Sorğu parametrləri
                params = {
                    "wait_for_model": "true",
                    "max_time": 120
                }
                
                # Sorğu göndər
                response = requests.post(
                    url, 
                    headers=headers, 
                    data=optimized_contents,
                    params=params,
                    timeout=120
                )
                
                print(f"Model: {name}, Status: {response.status_code}, Ölçü: {len(response.content)}")
                
                if response.status_code == 200 and len(response.content) > 1000:
                    # Unikal fayl adı yarat
                    filename = f"cartoon_{unique_id}_{name.replace(' ', '_')}.jpg"
                    filepath = f"/tmp/cartoon_images/{filename}"
                    
                    # Şəkli saxla
                    try:
                        result_image = Image.open(BytesIO(response.content))
                        result_image.save(filepath, "JPEG", quality=95)
                        results.append((name, filename))
                        print(f"Uğurlu: {name}")
                    except Exception as e:
                        print(f"Şəkil saxlanarkən xəta: {e}")
                        continue
                else:
                    print(f"Model cavab vermədi: {name}, Status: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                print(f"Model zaman aşımı: {name}")
                continue
            except Exception as e:
                print(f"Model xətası {name}: {e}")
                continue

        if not results:
            return HTMLResponse("""
            <html>
            <head>
                <title>Xəta - Karikatura Çevirici</title>
                <style>
                    body { 
                        font-family: Arial; 
                        text-align: center; 
                        margin-top: 100px; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .error-container {
                        background: rgba(255, 255, 255, 0.1);
                        padding: 40px;
                        border-radius: 20px;
                        backdrop-filter: blur(10px);
                        max-width: 600px;
                        margin: 0 auto;
                    }
                    .btn {
                        background: #ff6b6b;
                        color: white;
                        padding: 15px 30px;
                        text-decoration: none;
                        border-radius: 50px;
                        display: inline-block;
                        margin-top: 20px;
                        transition: all 0.3s ease;
                    }
                    .btn:hover {
                        background: #ff5252;
                        transform: translateY(-2px);
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1 style="color: #ffd700;">😔 Model Hazırlanır</h1>
                    <p style="font-size: 1.2em;">Modellər hazırda yüklənir və ya məşğuldur.</p>
                    <p>Zəhmət olmasa 1-2 dəqiqə sonra yenidən cəhd edin.</p>
                    <a href="/" class="btn">⬅ Yenidən cəhd et</a>
                </div>
            </body>
            </html>
            """)

        # Nəticələri göstər
        html = """
        <!DOCTYPE html>
        <html lang="az">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nəticələr - Karikatura Çevirici</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                h1 {
                    text-align: center;
                    color: #ffd700;
                    margin-bottom: 40px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }
                .results-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                    gap: 30px;
                    margin-bottom: 40px;
                }
                .result-card {
                    background: rgba(255, 255, 255, 0.1);
                    padding: 25px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                    transition: transform 0.3s ease;
                }
                .result-card:hover {
                    transform: translateY(-5px);
                }
                .result-card h3 {
                    color: #ffd700;
                    margin-bottom: 15px;
                }
                .result-card img {
                    width: 100%;
                    max-width: 350px;
                    height: auto;
                    border-radius: 15px;
                    border: 3px solid rgba(255, 255, 255, 0.2);
                }
                .download-btn {
                    background: #27ae60;
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 8px;
                    display: inline-block;
                    margin-top: 15px;
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                    font-size: 16px;
                }
                .download-btn:hover {
                    background: #219653;
                    transform: translateY(-2px);
                }
                .back-btn {
                    background: #3498db;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    display: inline-block;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                    font-size: 18px;
                }
                .back-btn:hover {
                    background: #2980b9;
                    transform: translateY(-2px);
                }
                .center {
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 Nəticələr Hazırdır!</h1>
                <div class="results-grid">
        """

        for name, filename in results:
            html += f"""
                    <div class="result-card">
                        <h3>{name}</h3>
                        <img src="/img/{filename}" alt="{name}">
                        <br>
                        <a href="/img/{filename}" download="{filename}" class="download-btn">
                            💾 Endir
                        </a>
                    </div>
            """

        html += """
                </div>
                <div class="center">
                    <a href="/" class="back-btn">🔄 Yenidən Çevir</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(html)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Ümumi xəta: {e}")
        raise HTTPException(status_code=500, detail="Daxili server xətası")

@app.get("/img/{filename}")
async def img(filename: str):
    filepath = f"/tmp/cartoon_images/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Şəkil tapılmadı")

# Köhnə faylları təmizləmək üçün funksiya
def cleanup_old_files():
    try:
        now = time.time()
        for filename in os.listdir("/tmp/cartoon_images"):
            filepath = os.path.join("/tmp/cartoon_images", filename)
            if os.path.isfile(filepath):
                # 1 saatdan köhnə faylları sil
                if now - os.path.getctime(filepath) > 3600:
                    os.remove(filepath)
    except Exception as e:
        print(f"Təmizləmə xətası: {e}")

if __name__ == "__main__":
    import uvicorn
    # Server başlayanda köhnə faylları təmizlə
    cleanup_old_files()
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
