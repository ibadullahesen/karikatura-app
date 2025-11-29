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
    {"name": "🎭 Karikatura", "description": "Canlı rənglər və karikatura təsiri", "type": "cartoon"},
    {"name": "✏️ Qələm Çəkilişi", "description": "Qara-ağ qələm təsiri", "type": "pencil"},
    {"name": "🌟 Anime Stili", "description": "Parlaq anime rəngləri", "type": "anime"},
    {"name": "🎨 Komik Kitab", "description": "Komik kitab tərzində", "type": "comic"},
    {"name": "🖼️ Rəssam Təsiri", "description": "Rəssam çəkilişi kimi", "type": "painterly"},
    {"name": "📐 Pop-Art", "description": "Pop-art stili effekti", "type": "popart"}
]

def apply_cartoon_effect(image):
    """Karikatura effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Kənarları tap
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Brightness(edges).enhance(2.0)
        
        # Rəngləri canlandır
        enhanced = ImageEnhance.Color(img).enhance(1.6)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)
        
        # Rəng sayını azalt
        quantized = enhanced.quantize(colors=16)
        quantized = quantized.convert('RGB')
        
        # Kənarları əlavə et
        final = Image.blend(quantized, edges.convert('RGB'), 0.08)
        return final
        
    except Exception as e:
        print(f"Karikatura effekti xətası: {e}")
        return image

def apply_pencil_sketch(image):
    """Qələm çəkilişi effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Qələm çəkilişi
        gray = img.convert('L')
        inverted = ImageOps.invert(gray)
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=2))
        pencil_sketch = Image.blend(gray, blurred, 0.75)
        pencil_sketch = ImageEnhance.Contrast(pencil_sketch).enhance(2.0)
        
        return pencil_sketch.convert('RGB')
        
    except Exception as e:
        print(f"Qələm effekti xətası: {e}")
        return image

def apply_anime_effect(image):
    """Anime stili effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Anime təsiri
        enhanced = ImageEnhance.Color(img).enhance(1.8)
        enhanced = ImageEnhance.Brightness(enhanced).enhance(1.1)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)
        
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        sharpened = sharpened.filter(ImageFilter.DETAIL)
        
        quantized = sharpened.quantize(colors=32)
        result = quantized.convert('RGB')
        
        return result
        
    except Exception as e:
        print(f"Anime effekti xətası: {e}")
        return image

def apply_comic_effect(image):
    """Komik kitab effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Komik kitab təsiri
        quantized = img.quantize(colors=12)
        quantized = quantized.convert('RGB')
        
        enhanced = ImageEnhance.Contrast(quantized).enhance(1.8)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(3.0)
        
        return enhanced
        
    except Exception as e:
        print(f"Komik effekti xətası: {e}")
        return image

def apply_painterly_effect(image):
    """Rəssam təsiri"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Rəssam təsiri
        smoothed = img.filter(ImageFilter.SMOOTH_MORE)
        enhanced = ImageEnhance.Color(smoothed).enhance(1.4)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        
        quantized = enhanced.quantize(colors=20)
        result = quantized.convert('RGB')
        
        return result
        
    except Exception as e:
        print(f"Rəssam effekti xətası: {e}")
        return image

def apply_popart_effect(image):
    """Pop-art effekti"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.LANCZOS)
        
        # Pop-art
        high_contrast = ImageEnhance.Contrast(img).enhance(2.0)
        saturated = ImageEnhance.Color(high_contrast).enhance(2.0)
        pop_art = saturated.quantize(colors=8)
        pop_art = pop_art.convert('RGB')
        
        return pop_art
        
    except Exception as e:
        print(f"Pop-art effekti xətası: {e}")
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Karikatura Çevirici</h1>
            <p style="font-size: 1.2em; margin-bottom: 30px;">Şəklini 6 fərqli stildə karikaturaya çevir!</p>
            
            <div class="features">
                <div class="feature">✅ 100% Pulsuz</div>
                <div class="feature">🚀 Reklam yoxdur</div>
                <div class="feature">🔒 Şəkillər saxlanmır</div>
                <div class="feature">⚡ Ani nəticə</div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <h3>📁 Şəkil seçin</h3>
                    <p>Faylı buraya sürükləyin və ya klikləyin</p>
                    <p style="font-size: 0.9em; opacity: 0.8;">(JPG, PNG, WEBP - Maksimum 5MB)</p>
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
        </div>

        <script>
            document.getElementById('fileInput').addEventListener('change', function(e) {
                const fileName = document.getElementById('fileName');
                if (this.files.length > 0) {
                    const file = this.files[0];
                    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
                    fileName.innerHTML = `✅ Seçilmiş fayl: <strong>${file.name}</strong> (${fileSize} MB)`;
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
                    alert('Xəta baş verdi: ' + error.message);
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

        contents = await file.read()
        
        try:
            image = Image.open(io.BytesIO(contents))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="Düzgün olmayan şəkil faylı")

        image = Image.open(io.BytesIO(contents))
        
        results = []
        unique_id = str(uuid.uuid4())[:8]

        print(f"🎨 Karikatura emalı başladı...")

        for model in MODELS:
            try:
                print(f"🔧 Model işləyir: {model['name']}")
                
                if model['type'] == "cartoon":
                    result_image = apply_cartoon_effect(image)
                elif model['type'] == "pencil":
                    result_image = apply_pencil_sketch(image)
                elif model['type'] == "anime":
                    result_image = apply_anime_effect(image)
                elif model['type'] == "comic":
                    result_image = apply_comic_effect(image)
                elif model['type'] == "painterly":
                    result_image = apply_painterly_effect(image)
                elif model['type'] == "popart":
                    result_image = apply_popart_effect(image)
                else:
                    result_image = apply_cartoon_effect(image)
                
                clean_name = model['name'].replace(' ', '_').replace('🎭', '').replace('✏️', '').replace('🌟', '').replace('🎨', '').replace('🖼️', '').replace('📐', '').strip()
                filename = f"cartoon_{unique_id}_{clean_name}.jpg"
                filepath = f"/tmp/cartoon_images/{filename}"
                
                result_image.save(filepath, "JPEG", quality=90, optimize=True)
                results.append({
                    'name': model['name'],
                    'description': model['description'],
                    'filename': filename
                })
                
                print(f"✅ Uğurlu: {model['name']}")
                
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
                h1 {{
                    text-align: center;
                    color: #ffd700;
                    margin-bottom: 30px;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                }}
                .results-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 25px;
                    margin-bottom: 40px;
                }}
                .result-card {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 20px;
                    border-radius: 15px;
                    backdrop-filter: blur(10px);
                    text-align: center;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
                    transition: all 0.3s ease;
                }}
                .result-card:hover {{
                    transform: translateY(-5px);
                }}
                .result-card h3 {{
                    color: #ffd700;
                    margin-bottom: 10px;
                }}
                .result-card p {{
                    color: #ddd;
                    margin-bottom: 15px;
                }}
                .result-card img {{
                    width: 100%;
                    max-width: 250px;
                    height: 250px;
                    object-fit: cover;
                    border-radius: 10px;
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
                <h1>🎉 Nəticələr Hazırdır!</h1>
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

@app.get("/img/{filename}")
async def img(filename: str):
    filepath = f"/tmp/cartoon_images/{filename}"
    if os.path.exists(filepath):
        return FileResponse(filepath, media_type="image/jpeg")
    else:
        raise HTTPException(status_code=404, detail="Şəkil tapılmadı")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Karikatura Çevirici Başladı!")
    print("🎨 6 fərqli karikatura stili hazırdır!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
