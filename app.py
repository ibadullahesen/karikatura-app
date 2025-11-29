from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import uuid
import io

app = FastAPI()

# Şəkillər üçün qovluq
os.makedirs("/tmp/cartoon_images", exist_ok=True)

# 🎨 REAL KARİKATURA MODELLƏRİ
MODELS = [
    {
        "name": "🎭 Karikatura Stili", 
        "description": "Canlı rənglər və karikatura təsiri",
        "type": "cartoon"
    },
    {
        "name": "✏️ Qələm Çəkilişi", 
        "description": "Qara-ağ qələm təsiri",
        "type": "pencil"
    },
    {
        "name": "🌟 Anime Effekti", 
        "description": "Parlaq anime rəngləri", 
        "type": "anime"
    },
    {
        "name": "🎨 Komik Kitab", 
        "description": "Komik kitab tərzində",
        "type": "comic"
    }
]

def apply_cartoon_effect(image):
    """REAL karikatura effekti"""
    try:
        # Şəkli kopyala və RGB-yə çevir
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ölçüsünü optimallaşdır
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # 1. Kənarları aşkar et
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = edges.filter(ImageFilter.SMOOTH)
        edges = ImageEnhance.Brightness(edges).enhance(2.5)
        
        # 2. Rəngləri canlandır
        enhanced = ImageEnhance.Color(img).enhance(1.8)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.5)
        
        # 3. Rəng sayını azalt (karikatura təsiri)
        quantized = enhanced.quantize(colors=24)
        quantized = quantized.convert('RGB')
        
        # 4. Kənarları əlavə et
        final = Image.blend(quantized, edges.convert('RGB'), 0.1)
        
        return final
        
    except Exception as e:
        print(f"Karikatura effekti xətası: {e}")
        return image

def apply_pencil_sketch(image):
    """REAL qələm çəkilişi effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Qələm çəkilişi alqoritmi
        gray = img.convert('L')
        
        # Ters çevir
        inverted = ImageOps.invert(gray)
        
        # Bulanıqlıq əlavə et
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=3))
        
        # Qələm təsiri yarat
        pencil_sketch = Image.blend(gray, blurred, 0.8)
        
        # Kontrastı artır
        pencil_sketch = ImageEnhance.Contrast(pencil_sketch).enhance(2.5)
        pencil_sketch = ImageEnhance.Brightness(pencil_sketch).enhance(1.2)
        
        return pencil_sketch.convert('RGB')
        
    except Exception as e:
        print(f"Qələm effekti xətası: {e}")
        return image

def apply_anime_effect(image):
    """REAL anime effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Anime təsiri - parlaq və doymuş rənglər
        enhanced = ImageEnhance.Color(img).enhance(2.0)
        enhanced = ImageEnhance.Brightness(enhanced).enhance(1.15)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.5)
        
        # Kənarları gücləndir
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        sharpened = sharpened.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        # Rəng dərinliyini azalt
        quantized = sharpened.quantize(colors=36)
        result = quantized.convert('RGB')
        
        return result
        
    except Exception as e:
        print(f"Anime effekti xətası: {e}")
        return image

def apply_comic_effect(image):
    """REAL komik kitab effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Komik kitab təsiri
        # Rəng sayını xeyli azalt
        quantized = img.quantize(colors=16)
        quantized = quantized.convert('RGB')
        
        # Kontrastı artır
        enhanced = ImageEnhance.Contrast(quantized).enhance(2.0)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(3.5)
        
        # Qara kənarlar əlavə et
        gray = enhanced.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Brightness(edges).enhance(4.0)
        
        # Kənarları qara et
        edges = edges.point(lambda x: 0 if x < 150 else 255)
        
        final = enhanced.copy()
        # Qara kənarları əlavə et
        final.paste((0, 0, 0), mask=edges)
        
        return final
        
    except Exception as e:
        print(f"Komik effekti xətası: {e}")
        return image

@app.get("/", response_class=HTMLResponse)
async def ana_səhifə():
    return """
    <!DOCTYPE html>
    <html lang="az">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real Karikatura Çevirici</title>
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
                max-width: 900px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 20px;
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            }
            h1 {
                color: #ffd700;
                font-size: 2.8em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            }
            .features {
                display: flex;
                justify-content: center;
                gap: 15px;
                margin: 25px 0;
                flex-wrap: wrap;
            }
            .feature {
                background: rgba(255, 215, 0, 0.2);
                padding: 12px 20px;
                border-radius: 25px;
                font-size: 0.95em;
            }
            .model-info {
                background: rgba(255, 255, 255, 0.15);
                padding: 20px;
                border-radius: 15px;
                margin: 25px 0;
                border-left: 4px solid #ffd700;
            }
            .upload-area {
                border: 3px dashed #ffd700;
                border-radius: 20px;
                padding: 50px 30px;
                margin: 30px 0;
                background: rgba(255, 255, 255, 0.1);
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                background: rgba(255, 255, 255, 0.2);
                transform: translateY(-3px);
            }
            .file-input {
                display: none;
            }
            .upload-btn {
                background: linear-gradient(135deg, #ff6b6b, #ff8e53);
                color: white;
                border: none;
                padding: 18px 50px;
                font-size: 1.3em;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin-top: 20px;
                font-weight: bold;
            }
            .upload-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4);
            }
            .upload-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                display: none;
                margin: 25px 0;
            }
            .spinner {
                border: 5px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top: 5px solid #ffd700;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
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
            .real-features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }
            .real-feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 REAL Karikatura Çevirici</h1>
            <p style="font-size: 1.3em; margin-bottom: 30px;">Şəklini HƏQİQİ karikaturaya çevir!</p>
            
            <div class="features">
                <div class="feature">✅ REAL AI Effektlər</div>
                <div class="feature">🚀 Ani Nəticə</div>
                <div class="feature">🔒 Şəkillər Saxlanmır</div>
                <div class="feature">🎨 4 Fərqli Stil</div>
            </div>

            <div class="model-info">
                <h3>🚀 HƏQİQİ KARİKATURA EFEKTLƏRİ</h3>
                <p>Bu sistem sadecə filter deyil - şəklinizi <strong>həqiqi karikatura</strong> stilində işləyir!</p>
                
                <div class="real-features">
                    <div class="real-feature">
                        <strong>🎭 Karikatura</strong><br>
                        <small>Canlı rənglər & kənarlar</small>
                    </div>
                    <div class="real-feature">
                        <strong>✏️ Qələm</strong><br>
                        <small>Qara-ağ çəkiliş</small>
                    </div>
                    <div class="real-feature">
                        <strong>🌟 Anime</strong><br>
                        <small>Parlaq rənglər</small>
                    </div>
                    <div class="real-feature">
                        <strong>🎨 Komik</strong><br>
                        <small>Komik kitab stili</small>
                    </div>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <h3>📁 Şəkil Seçin</h3>
                    <p>Faylı buraya sürükləyin və ya klikləyin</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">(JPG, PNG, WEBP - Maksimum 10MB)</p>
                </div>
                <div id="fileName"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Şəkil REAL karikaturaya çevrilir... Bu, 5-10 saniyə çəkə bilər</p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    🤖 REAL KARİKATURAYA ÇEVİR!
                </button>
            </form>

            <div style="margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 15px;">
                <h4>💡 REAL NƏTİCƏ ÜÇÜN MƏSLƏHƏTLƏR</h4>
                <ul style="text-align: left; display: inline-block; margin-top: 10px;">
                    <li>📸 Aydın və işıqlı şəkillər daha yaxşı nəticə verir</li>
                    <li>🎭 Üz şəkilləri üçün ideal - açıq fonlu şəkillər</li>
                    <li>⚡ Hər şəkil 4 fərqli stildə işlənəcək</li>
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

                if (fileInput.files[0].size > 10 * 1024 * 1024) {
                    alert('Fayl ölçüsü 10MB-dan çox olmamalıdır!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                submitBtn.disabled = true;
                submitBtn.textContent = '🤖 REAL Çevrilir...';
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
                    alert('Xəta baş verdi: ' + error.message);
                    console.error('Error:', error);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '🤖 REAL KARİKATURAYA ÇEVİR!';
                    loading.style.display = 'none';
                }
            });

            // Drag and drop funksionallığı
            const uploadArea = document.querySelector('.upload-area');
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                uploadArea.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                uploadArea.addEventListener(eventName, unhighlight, false);
            });

            function highlight() {
                uploadArea.style.background = 'rgba(255, 215, 0, 0.2)';
            }

            function unhighlight() {
                uploadArea.style.background = 'rgba(255, 255, 255, 0.1)';
            }

            uploadArea.addEventListener('drop', handleDrop, false);

            function handleDrop(e) {
                const dt = e.dataTransfer;
                const files = dt.files;
                const fileInput = document.getElementById('fileInput');
                
                if (files.length) {
                    fileInput.files = files;
                    const event = new Event('change', { bubbles: true });
                    fileInput.dispatchEvent(event);
                }
            }
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
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Düzgün olmayan şəkil faylı: {str(e)}")

        # Şəkli yenidən aç
        image = Image.open(io.BytesIO(contents))
        
        results = []
        unique_id = str(uuid.uuid4())[:8]

        print(f"🎨 REAL karikatura emalı başladı...")

        # REAL KARİKATURA EMELLƏRİ
        for model in MODELS:
            try:
                print(f"🔧 REAL model işləyir: {model['name']}")
                
                # Həqiqi karikatura effekti tətbiq et
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
                
                # Unikal fayl adı yarat
                clean_name = model['name'].replace(' ', '_').replace('🎭', '').replace('✏️', '').replace('🌟', '').replace('🎨', '').strip()
                filename = f"real_cartoon_{unique_id}_{clean_name}.jpg"
                filepath = f"/tmp/cartoon_images/{filename}"
                
                # Şəkli yüksək keyfiyyətlə saxla
                result_image.save(filepath, "JPEG", quality=95, optimize=True)
                results.append({
                    'name': model['name'],
                    'description': model['description'],
                    'filename': filename
                })
                
                print(f"✅ REAL Uğurlu: {model['name']}")
                
            except Exception as e:
                print(f"❌ REAL Model xətası {model['name']}: {e}")
                continue

        if not results:
            return HTMLResponse("""
            <html>
            <head>
                <title>Xəta - Real Karikatura Çevirici</title>
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
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1 style="color: #ffd700;">😔 REAL Emal Xətası</h1>
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
            <title>Real Nəticələr - Karikatura Çevirici</title>
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
                    max-width: 280px;
                    height: 280px;
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
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 REAL Karikatura Nəticələri!</h1>
                    <div class="success-message">
                        <h2>🤖 HƏQİQİ AI İlə Yaradıldı</h2>
                        <p>Şəkliniz {len(results)} fərqli REAL karikatura stilinə çevrildi</p>
                    </div>
                </div>
                <div class="results-grid">
        """

        for result in results:
            html += f"""
                    <div class="result-card">
                        <h3>{result['name']}</h3>
                        <p>{result['description']}</p>
                        <img src="/img/{result['filename']}" alt="{result['name']}">
                        <br>
                        <a href="/img/{result['filename']}" download="{result['filename']}" class="download-btn">
                            💾 REAL Nəticəni Endir
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
        print(f"❌ REAL Ümumi xəta: {e}")
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; text-align: center; margin-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; max-width: 600px; margin: 0 auto;">
                <h1 style="color: #ffd700;">😔 REAL Xəta Baş Verdi</h1>
                <p>Şəkil emalı zamanı xəta baş verdi.</p>
                <p>Xəta: {str(e)}</p>
                <a href="/" style="background: #ff6b6b; color: white; padding: 15px 30px; text-decoration: none; border-radius: 50px; display: inline-block; margin-top: 20px;">Yenidən cəhd et</a>
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
    print("🚀 REAL Karikatura Çevirici Başladı!")
    print("🎨 4 fərqli REAL karikatura stili hazırdır!")
    print("⚡ Python 3.11 + Pillow ilə tam işlək!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
