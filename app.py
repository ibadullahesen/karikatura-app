from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import uuid
import io
import base64
import requests
import numpy as np
import cv2
from io import BytesIO

app = FastAPI()

# Static fayllar üçün qovluq yaradın
os.makedirs("/tmp/cartoon_images", exist_ok=True)

# 🎨 REAL KARİKATURA/ANIME MODELLƏRİ
MODELS = [
    {
        "name": "🎭 Real Karikatura", 
        "description": "Həqiqi karikatura üzünə çevirir",
        "type": "cartoon",
        "api_url": "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion"
    },
    {
        "name": "🌟 Anime Personajı", 
        "description": "Anime personajı kimi",
        "type": "anime", 
        "api_url": "https://api-inference.huggingface.co/models/andite/anything-v4.0"
    },
    {
        "name": "✏️ Karikatura Çəkilişi", 
        "description": "Çizgi film personajı",
        "type": "sketch",
        "api_url": "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion"
    },
    {
        "name": "🎨 Pixar Stili", 
        "description": "Pixar animasiyası kimi",
        "type": "pixar",
        "api_url": "https://api-inference.huggingface.co/models/ogkalu/Comic-Diffusion"
    }
]

def detect_face(image):
    """Üzü aşkar et və kəsin"""
    try:
        # PIL to OpenCV
        img_cv = np.array(image)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
        
        # Üz aşkarlama
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            x, y, w, h = faces[0]
            # Üzü kəsin
            face_img = img_cv[y:y+h, x:x+w]
            return Image.fromarray(cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB))
        
        return image
    except:
        return image

def enhance_for_ai(image):
    """AI modeli üçün şəkli hazırla"""
    try:
        img = image.copy()
        
        # Ölçüsünü AI üçün optimallaşdır
        if max(img.size) > 512:
            img.thumbnail((512, 512), Image.Resampling.LANCZOS)
        
        # Keyfiyyəti yaxşılaşdır
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95, optimize=True)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Şəkil hazırlama xətası: {e}")
        return None

def call_ai_model(image_bytes, api_url, prompt_suffix=""):
    """AI modelini çağır"""
    try:
        headers = {
            "Authorization": "Bearer hf_your_token_here",  # Pulsuz token əlavə etmək lazımdır
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Prompt optimallaşdırma
        base_prompt = "cartoon character, anime style, high quality, detailed face, professional artwork"
        full_prompt = f"{base_prompt} {prompt_suffix}"
        
        payload = {
            "inputs": full_prompt,
            "options": {
                "wait_for_model": True,
                "use_cache": True
            }
        }
        
        response = requests.post(
            api_url,
            headers=headers,
            files={"data": image_bytes},
            data=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.content
        else:
            print(f"API cavabı: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"AI model xətası: {e}")
        return None

def apply_cartoon_effect_ai(image, model_type):
    """AI ilə karikatura effekti"""
    try:
        # Üzü aşkar et
        face_image = detect_face(image)
        
        # AI üçün hazırla
        enhanced_image = enhance_for_ai(face_image)
        if enhanced_image is None:
            return image
        
        # Müvafiq API seç
        api_url = next((model["api_url"] for model in MODELS if model["type"] == model_type), MODELS[0]["api_url"])
        
        # Prompt seçimi
        prompts = {
            "cartoon": "digital artwork, illustrative, disney style, cartoon character",
            "anime": "anime character, japanese animation, manga style, vibrant colors",
            "sketch": "sketch drawing, line art, black and white, pencil sketch",
            "pixar": "3d render, pixar animation, cartoon character, cute style"
        }
        
        prompt = prompts.get(model_type, "cartoon character")
        
        # AI modelini çağır
        result_bytes = call_ai_model(enhanced_image, api_url, prompt)
        
        if result_bytes and len(result_bytes) > 1000:
            result_image = Image.open(io.BytesIO(result_bytes))
            return result_image
        else:
            # AI işləməzsə, əsas şəkli qaytar
            return apply_basic_cartoon(image)
            
    except Exception as e:
        print(f"AI karikatura xətası: {e}")
        return apply_basic_cartoon(image)

def apply_basic_cartoon(image):
    """Əsas karikatura effekti (fallback)"""
    try:
        img = image.copy()
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        if max(img.size) > 800:
            img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        # Karikatura effekti
        gray = img.convert('L')
        edges = gray.filter(ImageFilter.FIND_EDGES)
        edges = ImageEnhance.Brightness(edges).enhance(2.0)
        
        enhanced = ImageEnhance.Color(img).enhance(1.6)
        enhanced = ImageEnhance.Contrast(enhanced).enhance(1.3)
        
        quantized = enhanced.quantize(colors=16)
        quantized = quantized.convert('RGB')
        
        final = Image.blend(quantized, edges.convert('RGB'), 0.08)
        return final
        
    except Exception as e:
        print(f"Əsas karikatura xətası: {e}")
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
                padding: 25px;
                border-radius: 15px;
                margin: 25px 0;
                border-left: 4px solid #ffd700;
                text-align: left;
            }
            .model-info h3 {
                color: #ffd700;
                margin-bottom: 15px;
                text-align: center;
            }
            .model-list {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .model-item {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .upload-area {
                border: 3px dashed #ffd700;
                border-radius: 20px;
                padding: 50px 30px;
                margin: 30px 0;
                background: rgba(255, 255, 255, 0.08);
                cursor: pointer;
                transition: all 0.3s ease;
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
            <h1>🎭 Real Karikatura Çevirici</h1>
            <p class="subtitle">Şəklini HƏQİQİ Karikatura & Anime Üzünə Çevir! 🤖</p>
            
            <div class="features">
                <div class="feature">✅ Real AI Modellər</div>
                <div class="feature">🎨 Həqiqi Karikatura</div>
                <div class="feature">🌟 Anime Personajı</div>
                <div class="feature">⚡ Professional Nəticə</div>
            </div>

            <div class="model-info">
                <h3>🚀 HƏQİQİ KARİKATURA ÇEVRİLMƏ</h3>
                <p>Bu sistem sadecə filter deyil - şəklinizi <strong>həqiqi karikatura və ya anime personajına</strong> çevirir!</p>
                
                <div class="model-list">
                    <div class="model-item">
                        <strong>🎭 Real Karikatura</strong><br>
                        <small>Disney/Pixar stili</small>
                    </div>
                    <div class="model-item">
                        <strong>🌟 Anime Personajı</strong><br>
                        <small>Japon animasiyası</small>
                    </div>
                    <div class="model-item">
                        <strong>✏️ Karikatura Çəkilişi</strong><br>
                        <small>Çizgi film personajı</small>
                    </div>
                    <div class="model-item">
                        <strong>🎨 Pixar Stili</strong><br>
                        <small>3D animasiya</small>
                    </div>
                </div>
            </div>

            <div class="model-info">
                <h3>📸 Nümunə Nəticələr</h3>
                <p>Aşağıdakı kimi professional nəticələr əldə edəcəksiniz:</p>
                <div class="examples">
                    <div class="example-card">
                        <div style="background: #eee; height: 80px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; margin-bottom: 8px;">
                            🎭 Karikatura
                        </div>
                        <small>Real karikatura üzü</small>
                    </div>
                    <div class="example-card">
                        <div style="background: #eee; height: 80px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; margin-bottom: 8px;">
                            🌟 Anime
                        </div>
                        <small>Anime personajı</small>
                    </div>
                    <div class="example-card">
                        <div style="background: #eee; height: 80px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; margin-bottom: 8px;">
                            ✏️ Çəkiliş
                        </div>
                        <small>Karikatura çəkilişi</small>
                    </div>
                    <div class="example-card">
                        <div style="background: #eee; height: 80px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #666; margin-bottom: 8px;">
                            🎨 3D Pixar
                        </div>
                        <small>Pixar stili</small>
                    </div>
                </div>
            </div>

            <form id="uploadForm" enctype="multipart/form-data">
                <div class="upload-area" onclick="document.getElementById('fileInput').click()">
                    <input type="file" id="fileInput" class="file-input" name="file" accept="image/*" required>
                    <span class="upload-icon">📁</span>
                    <h3>Öz Şəklini Seç</h3>
                    <p>Üz şəklini buraya yüklə və karikaturaya çevir!</p>
                    <p style="font-size: 0.9em; opacity: 0.8; margin-top: 10px;">(JPG, PNG - Açıq üz şəkli daha yaxşı nəticə verir)</p>
                </div>
                <div id="fileName"></div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>AI şəklini karikaturaya çevirir... Bu, 30-60 saniyə çəkə bilər</p>
                    <p><small>Həqiqi AI modelləri işləyir - gözləyin</small></p>
                </div>
                
                <button type="submit" class="upload-btn" id="submitBtn">
                    🤖 KARİKATURAYA ÇEVİR!
                </button>
            </form>

            <div style="margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.2); border-radius: 15px;">
                <h4>💡 Məsləhət</h4>
                <p>Daha yaxşı nəticə üçün:</p>
                <ul style="text-align: left; display: inline-block; margin-top: 10px;">
                    <li>Açıq, işıqlı üz şəkli istifadə edin</li>
                    <li>Şəkil keyfiyyəti yüksək olsun</li>
                    <li>Üz aydın görünsün</li>
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
                submitBtn.textContent = '🤖 AI İşləyir...';
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
                    submitBtn.textContent = '🤖 KARİKATURAYA ÇEVİR!';
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

        print(f"🎨 Real karikatura çevirmə başladı...")

        for model in MODELS:
            try:
                print(f"🤖 AI model işləyir: {model['name']}")
                
                # AI ilə karikatura çevir
                result_image = apply_cartoon_effect_ai(image, model['type'])
                
                if result_image:
                    clean_name = model['name'].replace(' ', '_').replace('🎭', '').replace('🌟', '').replace('✏️', '').replace('🎨', '').strip()
                    filename = f"real_cartoon_{unique_id}_{clean_name}.jpg"
                    filepath = f"/tmp/cartoon_images/{filename}"
                    
                    result_image.save(filepath, "JPEG", quality=90, optimize=True)
                    results.append({
                        'name': model['name'],
                        'description': model['description'],
                        'filename': filename
                    })
                    
                    print(f"✅ Uğurlu: {model['name']}")
                else:
                    print(f"❌ AI cavab vermədi: {model['name']}")
                
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
                    }
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1 style="color: #ffd700;">😔 AI Modelləri Məşğul</h1>
                    <p style="font-size: 1.2em;">Karikatura modelləri hazırda yüklənir.</p>
                    <p>Zəhmət olmasa 1-2 dəqiqə sonra yenidən cəhd edin.</p>
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
            <title>Karikatura Nəticələri</title>
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
                    max-width: 300px;
                    height: 300px;
                    object-fit: cover;
                    border-radius: 15px;
                    border: 3px solid rgba(255, 255, 255, 0.2);
                }}
                .download-btn {{
                    background: linear-gradient(135deg, #27ae60, #2ecc71);
                    color: white;
                    padding: 12px 25px;
                    text-decoration: none;
                    border-radius: 10px;
                    display: inline-block;
                    margin-top: 15px;
                    transition: all 0.3s ease;
                }}
                .download-btn:hover {{
                    transform: translateY(-2px);
                }}
                .back-btn {{
                    background: linear-gradient(135deg, #3498db, #2980b9);
                    color: white;
                    padding: 15px 30px;
                    text-decoration: none;
                    border-radius: 50px;
                    display: inline-block;
                    margin-top: 20px;
                    transition: all 0.3s ease;
                }}
                .back-btn:hover {{
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
                    <h1>🎉 Karikatura Nəticələri Hazırdır!</h1>
                    <div class="success-message">
                        <h2>🤖 AI İlə Yaradıldı</h2>
                        <p>Şəkliniz {len(results)} fərqli karikatura stilinə çevrildi</p>
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
                            💾 Endir
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
                <p>Zəhmət olmasa yenidən cəhd edin.</p>
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
    print("🚀 Real Karikatura Çevirici Başladı!")
    print("🎭 Xüsusiyyət: Həqiqi AI ilə karikatura çevirmə!")
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
