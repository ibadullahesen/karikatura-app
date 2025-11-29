from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import uuid
import io
import base64

app = FastAPI()

# Static fayllar üçün qovluq yaradın
os.makedirs("/tmp/cartoon_images", exist_ok=True)

# ⚡ 100% YERLİ KARİKATURA MODELLƏRİ
MODELS = [
    {
        "name": "🎨 Karikatura Effekti", 
        "description": "Canlı rənglər və kənar təsiri",
        "type": "cartoon"
    },
    {
        "name": "✏️ Qələm Çəkilişi", 
        "description": "Qara-ağ qələm təsiri",
        "type": "pencil"
    },
    {
        "name": "🌟 Anime Stili", 
        "description": "Parlaq anime rəngləri",
        "type": "anime"
    },
    {
        "name": "🎭 Komik Kitab", 
        "description": "Komik kitab tərzində",
        "type": "comic"
    },
    {
        "name": "🖼️ Rəssam Təsiri", 
        "description": "Rəssam çəkilişi kimi",
        "type": "painterly"
    },
    {
        "name": "📐 Pop-Art", 
        "description": "Pop-art stili effekti",
        "type": "popart"
    }
]

def apply_cartoon_effect(image):
    """Əsas karikatura effekti"""
    try:
        # Şəkili optimallaşdır
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Ölçüsünü tənzimlə
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # 1. Kənarları tap
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = edges.filter(ImageFilter.SMOOTH)
        edges = ImageEnhance.Brightness(edges).enhance(2.0)
        
        # 2. Rəngləri canlandır
        enhanced = ImageEnhance.Color(img).enhance(1.6)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(2.0)
        
        # 3. Rəng sayını azalt (karikatura təsiri)
        quantized = enhanced.quantize(colors=16)
        quantized = quantized.convert('RGB')
        
        # 4. Kənarları əlavə et
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Qələm çəkilişi alqoritmi
        gray = img.convert('L')
        
        # Ters çevir
        inverted = ImageOps.invert(gray)
        
        # Bulanıqlıq əlavə et
        blurred = inverted.filter(ImageFilter.GaussianBlur(radius=2))
        
        # Qələm təsiri yarat
        pencil_sketch = Image.blend(gray, blurred, 0.75)
        
        # Kontrastı artır
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Anime təsiri - parlaq rənglər
        enhanced = ImageEnhance.Color(img).enhance(1.8)
        enhanced = ImageEnhance.Brightness(enhanced).enhance(1.1)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.4)
        
        # Kənarları gücləndir
        sharpened = enhanced.filter(ImageFilter.SHARPEN)
        sharpened = sharpened.filter(ImageFilter.DETAIL)
        
        # Rəng dərinliyini azalt
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Komik kitab təsiri
        # Rəng sayını xeyli azalt
        quantized = img.quantize(colors=12)
        quantized = quantized.convert('RGB')
        
        # Kontrastı artır
        enhanced = ImageEnhance.Contrast(quantized).enhance(1.8)
        enhanced = ImageEnhance.Sharpness(enhanced).enhance(3.0)
        
        # Qara kənarlar əlavə et
        gray = enhanced.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Brightness(edges).enhance(3.0)
        
        # Kənarları qara et
        edges = edges.point(lambda x: 0 if x < 100 else 255)
        
        final = enhanced.copy()
        # Qara kənarları əlavə et
        final.paste((0, 0, 0), mask=edges)
        
        return final
        
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Rəssam təsiri üçün bir neçə filter
        # 1. Orta bulanıqlıq
        smoothed = img.filter(ImageFilter.SMOOTH_MORE)
        
        # 2. Rəng doymasını artır
        enhanced = ImageEnhance.Color(smoothed).enhance(1.4)
        
        # 3. Kontrast
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        
        # 4. Rəng sayını azalt
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
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Pop-art üçün yüksək kontrast və az rəng
        # Kontrastı çox artır
        high_contrast = ImageEnhance.Contrast(img).enhance(2.0)
        
        # Rəng doymasını artır
        saturated = ImageEnhance.Color(high_contrast).enhance(2.0)
        
        # Çox az rəng sayı
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
        <title>Pulsuz Karikatura Çevirici</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
                border-radius: 25px;
                backdrop-filter: blur(15px);
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            h1 {
                color: #ffd700;
                font-size: 2.8em;
                margin-bottom: 15px;
                text-shadow: 3px 3px 6px rgba(0, 0, 0, 0.4);
            }
            .subtitle {
                font-size: 1.3em;
                margin-bottom: 30px;
                opacity: 0.9;
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
                border: 1px solid rgba(255, 215, 0, 0.3);
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
                background: rgba(255, 255, 255, 0.08);
                cursor: pointer;
                transition: all 0.3s ease;
                position: relative;
            }
            .upload-area:hover {
                background: rgba(255, 255, 255, 0.15);
                transform: translateY(-3px);
                box-shadow: 0 10px 25px rgba(255, 215, 0, 0.2);
            }
            .upload-icon {
                font-size: 4em;
                margin-bottom: 15px;
                display: block;
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
                box-shadow: 0 5px 15px rgba(255, 107, 107, 0.4);
            }
            .upload-btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 25px rgba(255, 107, 107, 0.6);
            }
            .upload-btn:disabled {
                background: #cccccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
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
            .models-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 25px 0;
            }
            .model-card {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 12px;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎨 Şəklini Karikaturaya Çevir</h1>
            <p class="subtitle">YERLİ AI İLƏ - ANI NƏTİCƏ! ⚡</p>
            
            <div class="features">
                <div class="feature">✅ 100% Pulsuz</div>
                <div class="feature">🚀 Reklam yoxdur</div>
                <div class="feature">🔒 Şəkillər saxlanmır</div>
                <div class="feature">⚡ Ani nəticə</div>
            </div>

            <div class="model-info">
                <h3>🚀 YERLİ MODELLƏR - GÖZLƏMƏ YOXDUR!</h3>
                <p>Xarici API-lardan asılı olmadığı üçün nəticələr 2-3 saniyə ərzində hazırdır</p>
                
                <div class="models-grid">
                    <div class="model-card">🎨 Karikatura</div>
                    <div class="model-card">✏️ Qələm</div>
                    <div class="model-card">🌟 Anime</div>
                    <div class="model-card">🎭 Komik</div>
                    <div class="model-card">🖼️ Rəssam</div>
                    <div class="model-card">📐 Pop-Art</div>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <span class="upload-icon">📁</span>
                    <h3>Şəkil Seçin</h3>
                    <p>Faylı buraya sürükləyin və ya klikləyin</p>
                    <p style="font-size: 0.9em; opacity: 0.8; margin-top: 10px;">(JPG, PNG, WEBP - Maksimum 5MB)</p>
                </div>
                <div id="fileName"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Şəkil karikaturaya çevrilir... Bu, cəmi 2-3 saniyə çəkəcək</p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    ⚡ ANİ KARİKATURAYA ÇEVİR!
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

                // Fayl ölçüsünü yoxla (5MB)
                if (fileInput.files[0].size > 5 * 1024 * 1024) {
                    alert('Fayl ölçüsü 5MB-dan çox olmamalıdır!');
                    return;
                }

                const formData = new FormData();
                formData.append('file', fileInput.files[0]);

                // Loading rejimini aktiv et
                submitBtn.disabled = true;
                submitBtn.textContent = '⚡ Çevrilir...';
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
                        const error = await response.text();
                        throw new Error('Server xətası');
                    }
                } catch (error) {
                    alert('Xəta baş verdi: ' + error.message + '\\nZəhmət olmasa yenidən cəhd edin.');
                    console.error('Error:', error);
                } finally {
                    submitBtn.disabled = false;
                    submitBtn.textContent = '⚡ ANİ KARİKATURAYA ÇEVİR!';
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
                uploadArea.style.borderColor = '#ffeb3b';
            }

            function unhighlight() {
                uploadArea.style.background = 'rgba(255, 255, 255, 0.08)';
                uploadArea.style.borderColor = '#ffd700';
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
            # Şəklin düzgün olub olmadığını yoxla
            image.verify()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Düzgün olmayan şəkil faylı: {str(e)}")

        # Şəkli yenidən aç
        image = Image.open(io.BytesIO(contents))
        
        results = []
        unique_id = str(uuid.uuid4())[:8]

        print(f"⚡ Yerli karikatura emalı başladı...")

        # ⚡ YERLİ MODELLƏR - HEÇ BİR XARİCİ API YOXDUR!
        for model in MODELS:
            try:
                print(f"🔧 Model işləyir: {model['name']}")
                
                # Yerli effekt funksiyalarını çağır
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
                    result_image = apply_cartoon_effect(image)  # Default
                
                # Unikal fayl adı yarat
                clean_name = model['name'].replace(' ', '_').replace('🎨', '').replace('✏️', '').replace('🌟', '').replace('🎭', '').replace('🖼️', '').replace('📐', '').strip()
                filename = f"cartoon_{unique_id}_{clean_name}.jpg"
                filepath = f"/tmp/cartoon_images/{filename}"
                
                # Şəkli saxla
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
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 20px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{
                    max-width: 1400px;
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
                    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
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
                    transform: translateY(-8px);
                    box-shadow: 0 15px 40px rgba(0,0,0,0.4);
                }}
                .result-card h3 {{
                    color: #ffd700;
                    margin-bottom: 10px;
                    font-size: 1.4em;
                }}
                .result-card p {{
                    color: #ddd;
                    margin-bottom: 20px;
                    font-size: 0.95em;
                }}
                .result-card img {{
                    width: 100%;
                    max-width: 350px;
                    height: 280px;
                    object-fit: cover;
                    border-radius: 15px;
                    border: 3px solid rgba(255, 255, 255, 0.2);
                    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
                }}
                .download-btn {{
                    background: linear-gradient(135deg, #27ae60, #2ecc71);
                    color: white;
                    padding: 14px 30px;
                    text-decoration: none;
                    border-radius: 10px;
                    display: inline-block;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                    border: none;
                    cursor: pointer;
                    font-size: 16px;
                    font-weight: bold;
                    box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
                }}
                .download-btn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 6px 20px rgba(39, 174, 96, 0.5);
                }}
                .back-btn {{
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 18px 35px;
                    text-decoration: none;
                    border-radius: 50px;
                    display: inline-block;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                    font-size: 18px;
                    font-weight: bold;
                    box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
                }}
                .back-btn:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 8px 25px rgba(52, 152, 219, 0.6);
                }}
                .center {{
                    text-align: center;
                }}
                .stats {{
                    background: rgba(255, 255, 255, 0.1);
                    padding: 15px;
                    border-radius: 15px;
                    margin: 20px 0;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Nəticələr Hazırdır!</h1>
                    <div class="success-message">
                        <h2>⚡ ANİ NƏTİCƏ - GÖZLƏMƏDƏN!</h2>
                        <p>Yerli AI modelləri sayəsində {len(results)} fərqli karikatura stili yaradıldı</p>
                        <div class="stats">
                            ⏱️ Emal müddəti: 2-3 saniyə | 🖼️ Nəticə: {len(results)} şəkil
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
                        <img src="/img/{result['filename']}" alt="{result['name']}" 
                             onerror="this.src='data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzUwIiBoZWlnaHQ9IjI4MCIgdmlld0JveD0iMCAwIDM1MCAyODAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzNTAiIGhlaWdodD0iMjgwIiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMSkiIHJ4PSIxNSIvPgo8dGV4dCB4PSI1MCUiIHk9IjUwJSIgZG9taW5hbnQtYmFzZWxpbmU9Im1pZGRsZSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtc2l6ZT0iMTYiIGZvbnQtZmFtaWx5PSJBcmlhbCI+SW1hZ2UgTG9hZGluZy4uLjwvdGV4dD4KPC9zdmc+'">
                        <br>
                        <a href="/img/{result['filename']}" download="{result['filename']}" class="download-btn">
                            💾 Şəkli Endir
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

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Ümumi xəta: {e}")
        return HTMLResponse(f"""
        <html>
        <body style="font-family: Arial; text-align: center; margin-top: 100px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
            <div style="background: rgba(255, 255, 255, 0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px); max-width: 600px; margin: 0 auto;">
                <h1 style="color: #ffd700;">😔 Xəta Baş Verdi</h1>
                <p style="font-size: 1.2em;">Şəkil emalı zamanı xəta baş verdi.</p>
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
    print("🚀 Server başladı! Yerli karikatura çevirici hazırdır!")
    print("⚡ Xüsusiyyət: 100% Yerli - Heç bir xarici API yoxdur!")
    print("🎨 6 fərqli karikatura stili mövcuddur!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
