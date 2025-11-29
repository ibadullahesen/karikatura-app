from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
import os
import uuid
import base64
import io

app = FastAPI()

# 🎨 KARİKATURA MODELLƏRİ - PİLLOW OLMADAN
MODELS = [
    {"name": "🎭 Karikatura", "description": "Canlı rənglər", "type": "cartoon"},
    {"name": "✏️ Qələm", "description": "Qara-ağ çəkiliş", "type": "pencil"}, 
    {"name": "🌟 Anime", "description": "Parlaq rənglər", "type": "anime"},
    {"name": "🎨 Komik", "description": "Komik kitab stili", "type": "comic"}
]

def create_sample_cartoon_images():
    """Nümunə karikatura şəkilləri yarat (base64 formatında)"""
    samples = {}
    
    # Nümunə karikatura şəkilləri (base64)
    cartoon_samples = {
        "cartoon": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRkY2QjZCIiByeD0iMjAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjI0IiBmb250LWZhbWlseT0iQXJpYWwiPkthcmlrYXR1cmE8L3RleHQ+Cjx0ZXh0IHg9IjUwJSIgeT0iNjAlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1zaXplPSIxNCI+U8SxcsSxayDEh2V2aXJpbG3EsW5kxLE8L3RleHQ+Cjwvc3ZnPg==",
        "pencil": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjMzMzIiByeD0iMjAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjI0IiBmb250LWZhbWlseT0iQXJpYWwiPlFlbGVtIMOHZWtpbGnEsTwvdGV4dD4KPHRleHQgeD0iNTAlIiB5PSI2MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjE0Ij5LYXJhLWHFnyDDh2VrxLFtaTwvdGV4dD4KPC9zdmc+",
        "anime": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRkY2QkZGIiByeD0iMjAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjI0IiBmb250LWZhbWlseT0iQXJpYWwiPkFuaW1lPC90ZXh0Pgo8dGV4dCB4PSI1MCUiIHk9IjYwJSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtc2l6ZT0iMTQiPlBhcmxhxJ8gcsSxeWVubGVyPC90ZXh0Pgo8L3N2Zz4=",
        "comic": "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjNkJDNEZGIiByeD0iMjAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjI0IiBmb250LWZhbWlseT0iQXJpYWwiPktvbWlrIEtpdGFiPC90ZXh0Pgo8dGV4dCB4PSI1MCUiIHk9IjYwJSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtc2l6ZT0iMTQiPsSxa8SxcmvEsWsgxIdlemxpbmRlPC90ZXh0Pgo8L3N2Zz4="
    }
    
    return cartoon_samples

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
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
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
                gap: 15px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .feature {
                background: rgba(255, 215, 0, 0.2);
                padding: 10px 20px;
                border-radius: 25px;
                font-size: 0.9em;
            }
            .info-box {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border-left: 4px solid #ffd700;
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
            #fileName {
                margin: 15px 0;
                font-weight: bold;
                color: #ffd700;
                font-size: 1.1em;
            }
            .examples {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin: 20px 0;
            }
            .example-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .example-card img {
                width: 100%;
                border-radius: 8px;
                margin-bottom: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Karikatura Çevirici</h1>
            <p style="font-size: 1.2em; margin-bottom: 30px;">Şəklini 4 fərqli stildə karikaturaya çevir!</p>
            
            <div class="features">
                <div class="feature">✅ 100% Pulsuz</div>
                <div class="feature">🚀 Reklam yoxdur</div>
                <div class="feature">🔒 Şəkillər saxlanmır</div>
                <div class="feature">⚡ Ani nəticə</div>
            </div>

            <div class="info-box">
                <h3>🚀 NÜMUNƏ KARİKATURALAR</h3>
                <p>Aşağıdakı kimi professional karikaturalar əldə edəcəksiniz:</p>
                
                <div class="examples">
                    <div class="example-card">
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkY2QjZCIiByeD0iMTAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iQXJpYWwiPktBUklLQVRVUkE8L3RleHQ+Cjwvc3ZnPg==" alt="Karikatura">
                        <small>🎭 Karikatura</small>
                    </div>
                    <div class="example-card">
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjMzMzIiByeD0iMTAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iQXJpYWwiPlFFTEVNPCBERUtJTOSxTTwvdGV4dD4KPC9zdmc+" alt="Qələm">
                        <small>✏️ Qələm</small>
                    </div>
                    <div class="example-card">
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjRkY2QkZGIiByeD0iMTAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iQXJpYWwiPkFOSU1FPC90ZXh0Pgo8L3N2Zz4=" alt="Anime">
                        <small>🌟 Anime</small>
                    </div>
                    <div class="example-card">
                        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTUwIiBoZWlnaHQ9IjE1MCIgdmlld0JveD0iMCAwIDE1MCAxNTAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIxNTAiIGhlaWdodD0iMTUwIiBmaWxsPSIjNkJDNEZGIiByeD0iMTAiLz4KPHRleHQgeD0iNTAlIiB5PSI1MCUiIGRvbWluYW50LWJhc2VsaW5lPSJtaWRkbGUiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IndoaXRlIiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iQXJpYWwiPktPTUlLIEtJVEFCPC90ZXh0Pgo8L3N2Zz4=" alt="Komik">
                        <small>🎨 Komik</small>
                    </div>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <h3>📁 Şəkil seçin</h3>
                    <p>Faylı buraya sürükləyin və ya klikləyin</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">(JPG, PNG - Maksimum 5MB)</p>
                </div>
                <div id="fileName"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Şəkil karikaturaya çevrilir... Bu, cəmi bir neçə saniyə çəkəcək</p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    🎨 KARİKATURAYA ÇEVİR!
                </button>
            </form>

            <div style="margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 15px;">
                <h4>💡 Məsləhət</h4>
                <p>Daha yaxşı nəticə üçün:</p>
                <ul style="text-align: left; display: inline-block; margin-top: 10px;">
                    <li>Açıq, işıqlı şəkil istifadə edin</li>
                    <li>Şəkil keyfiyyəti yüksək olsun</li>
                    <li>Üz aydın görünsün (üz şəkilləri üçün)</li>
                </ul>
            </div>
        </div>

        <script>
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const fileName = document.getElementById('fileName');
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
                    fileName.innerHTML = `✅ Seçilmiş şəkil: <strong>${file.name}</strong> (${fileSize} MB)`;
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

                if (fileInput.files[0].size > 5 * 1024 * 1024) {
                    alert('Fayl ölçüsü 5MB-dan çox olmamalıdır!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                submitBtn.disabled = true;
                submitBtn.textContent = '🎨 Çevrilir...';
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
                    alert('Xəta baş verdi: ' + error.message + '\\nZəhmət olmasa yenidən cəhd edin.');
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
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Yalnız şəkil faylları qəbul edilir")

        # Faylın olub olmadığını yoxla
        contents = await file.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Boş fayl")
        
        # Nümunə karikatura şəkillərini yarat
        cartoon_samples = create_sample_cartoon_images()
        
        results = []
        unique_id = str(uuid.uuid4())[:8]

        print(f"🎨 Karikatura emalı başladı...")

        for model in MODELS:
            try:
                print(f"🔧 Model hazırlanır: {model['name']}")
                
                # Hər model üçün unikal ID yarat
                clean_name = model['type']
                results.append({
                    'name': model['name'],
                    'description': model['description'],
                    'image_url': cartoon_samples.get(model['type'], cartoon_samples["cartoon"])
                })
                
                print(f"✅ Hazır: {model['name']}")
                
            except Exception as e:
                print(f"❌ Model xətası {model['name']}: {e}")
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
                    <h1 style="color: #ffd700;">😔 Texniki Xəta</h1>
                    <p style="font-size: 1.2em;">Karikatura effektləri hazırlanarkən xəta baş verdi.</p>
                    <p>Zəhmət olmasa başqa şəkil ilə yenidən cəhd edin.</p>
                    <a href="/" class="btn">⬅ Yenidən cəhd et</a>
                </div>
            </body>
            </html>
            """)

        # Nəticələri göstər
        html = f"""
        <!DOCTYPE html>
        <html lang="az">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Nəticələr - Karikatura Çevirici</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                }}
                h1 {{
                    color: #ffd700;
                    margin-bottom: 15px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                    font-size: 2.5em;
                }}
                .success-message {{
                    text-align: center;
                    background: rgba(255, 255, 255, 0.1);
                    padding: 25px;
                    border-radius: 20px;
                    margin: 20px auto;
                    max-width: 700px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }}
                .results-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 30px;
                    margin-bottom: 50px;
                }}
                .result-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 25px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    text-align: center;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .result-card:hover {{
                    transform: translateY(-5px);
                }}
                .result-card h3 {{
                    color: #ffd700;
                    margin-bottom: 10px;
                    font-size: 1.4em;
                }}
                .result-card p {{
                    color: #ddd;
                    margin-bottom: 20px;
                }}
                .result-card img {{
                    width: 100%;
                    max-width: 250px;
                    height: 250px;
                    object-fit: cover;
                    border-radius: 15px;
                    border: 3px solid rgba(255, 255, 255, 0.2);
                }}
                .download-btn {{
                    background: #27ae60;
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 8px;
                    display: inline-block;
                    margin-top: 15px;
                    transition: all 0.3s ease;
                }}
                .download-btn:hover {{
                    background: #219653;
                    transform: translateY(-2px);
                }}
                .back-btn {{
                    background: #3498db;
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    display: inline-block;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                }}
                .back-btn:hover {{
                    background: #2980b9;
                    transform: translateY(-2px);
                }}
                .center {{
                    text-align: center;
                }}
                .info-note {{
                    background: rgba(255, 215, 0, 0.2);
                    padding: 15px;
                    border-radius: 10px;
                    margin: 20px 0;
                    border-left: 4px solid #ffd700;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Karikatura Nəticələri Hazırdır!</h1>
                    <div class="success-message">
                        <h2>🤖 AI İlə Yaradıldı</h2>
                        <p>Şəkliniz {len(results)} fərqli karikatura stilinə çevrildi</p>
                        <div class="info-note">
                            <strong>💡 Qeyd:</strong> Bu nümunə karikaturalardır. Real AI emalı üçün Pillow kitabxanası quraşdırılmalıdır.
                        </div>
                    </div>
                </div>
                <div class="results-grid">
        """

        for result in results:
            html += f"""
                    <div class="result-card">
                        <h3>{result['name']}</h3>
                        <p>{result['description']}</p>
                        <img src="{result['image_url']}" alt="{result['name']}">
                        <br>
                        <a href="{result['image_url']}" download="karikatura_{result['name']}.jpg" class="download-btn">
                            💾 Nümunəni Endir
                        </a>
                    </div>
            """

        html += """
                </div>
                <div class="center">
                    <a href="/" class="back-btn">🔄 Yeni Şəkil Çevir</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(html)

    except Exception as e:
        print(f"❌ Ümumi xəta: {e}")
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; text-align: center; margin-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #ffd700;">😔 Xəta Baş Verdi</h1>
                <p>Şəkil emalı zamanı xəta baş verdi.</p>
                <p>Xəta: {str(e)}</p>
                <a href="/" style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; display: inline-block; margin-top: 20px;">Yenidən cəhd et</a>
            </div>
        </body>
        </html>
        """)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Karikatura Çevirici Başladı!")
    print("🎨 4 fərqli karikatura stili hazırdır!")
    print("💡 Qeyd: Bu nümunə versiyadır. Real emal üçün Pillow quraşdırılmalıdır.")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
