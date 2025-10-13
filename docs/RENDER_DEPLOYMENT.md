# Render.com Deployment Guide for FinanceML Pipeline

## 🚀 Render'da Ücretsiz Deployment

Render free tier ile backend API'nizi ve frontend'inizi ücretsiz deploy edebilirsiniz.

### Render Free Tier Özellikleri
- ✅ 750 saat/ay ücretsiz (tüm servisler toplamda)
- ✅ Otomatik SSL sertifikası
- ✅ GitHub entegrasyonu (auto-deploy)
- ✅ Custom domain desteği
- ⚠️ 15 dakika aktif olmama sonrası servis durur (cold start)
- ⚠️ Persistent disk yok (her deploy'da sıfırlanır)

---

## 📋 Deployment Adımları

### 1. GitHub Repository Hazırlığı

Repository'niz zaten public ve hazır olmalı. Eğer değilse:

```bash
git add .
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

### 2. Render Account Oluşturma

1. https://render.com adresine git
2. "Get Started" → "Sign up with GitHub"
3. GitHub Student Pack'iniz varsa, Render'da da education discount alabilirsiniz

### 3. Backend API Deployment

#### Manuel Yöntem:
1. Render Dashboard → "New +" → "Web Service"
2. GitHub repository'nizi bağla: `TunahanKicci/FinanceML-Pipeline`
3. Ayarları yapılandır:
   - **Name**: `financeml-api`
   - **Region**: Frankfurt (Avrupa için en yakın)
   - **Branch**: `main`
   - **Root Directory**: `.` (boş bırak)
   - **Environment**: `Docker`
   - **Dockerfile Path**: `./api/Dockerfile`
   - **Docker Context**: `.`
   - **Instance Type**: Free
   - **Health Check Path**: `/health`

4. Environment Variables ekle:
   ```
   PYTHONUNBUFFERED=1
   LOG_LEVEL=INFO
   PORT=8000
   ```

5. "Create Web Service" butonuna tıkla

#### Blueprint Yöntemi (Önerilen):
1. Render Dashboard → "New +" → "Blueprint"
2. Repository seç: `TunahanKicci/FinanceML-Pipeline`
3. `render.yaml` dosyası otomatik algılanacak
4. "Apply" butonuna tıkla
5. Her iki servis de otomatik oluşturulacak

### 4. Frontend Deployment

#### Manuel Yöntem:
1. Render Dashboard → "New +" → "Static Site"
2. GitHub repository'nizi bağla
3. Ayarları yapılandır:
   - **Name**: `financeml-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install --legacy-peer-deps && npm run build`
   - **Publish Directory**: `build`

4. Environment Variables:
   ```
   REACT_APP_API_URL=https://financeml-api.onrender.com
   ```
   *(API URL'inizi kendi URL'inizle değiştirin)*

5. "Create Static Site" butonuna tıkla

### 5. Deploy Sonrası Kontrol

API deploy edildikten sonra:
```bash
curl https://financeml-api.onrender.com/health
```

Frontend deploy edildikten sonra:
```
https://financeml-frontend.onrender.com
```

---

## 🌐 GitHub Student Pack ile Domain Alma

### 1. GitHub Student Pack'i Aktifleştir

1. https://education.github.com/pack adresine git
2. "Get the Pack" → Öğrenci belgelerini yükle
3. Onay bekle (genellikle 1-2 gün)

### 2. Ücretsiz Domain Seçenekleri

GitHub Student Pack'te şu domain sağlayıcıları var:

#### **Namecheap** (Önerilen)
- ✅ 1 yıl ücretsiz .me domain
- ✅ SSL sertifikası dahil
- ✅ DNS yönetimi kolay

**Adımlar**:
1. https://nc.me adresine git
2. GitHub Student Pack linki kullan
3. .me domain ara: `financeml.me`, `yourusername-ml.me` vb.
4. Activate student discount
5. Domain'i satın al (1 yıl ücretsiz)

#### **Name.com**
- ✅ 1 yıl ücretsiz .me domain
- Namecheap'e alternatif

#### **.tech Domains**
- ✅ 1 yıl ücretsiz .tech domain
- ML/AI projeleri için uygun: `financeml.tech`

### 3. Domain'i Render'a Bağlama

#### API için:
1. Render Dashboard → `financeml-api` service
2. "Settings" → "Custom Domain"
3. "Add Custom Domain" → `api.yourdomain.me` gir
4. DNS kayıtlarını kopyala

#### Domain DNS Ayarları (Namecheap):
1. Namecheap Dashboard → Domain List → Manage
2. "Advanced DNS" sekmesi
3. Şu kayıtları ekle:

```
Type: CNAME
Host: api
Value: financeml-api.onrender.com
TTL: Automatic
```

```
Type: CNAME
Host: www
Value: financeml-frontend.onrender.com
TTL: Automatic
```

```
Type: CNAME
Host: @
Value: financeml-frontend.onrender.com
TTL: Automatic
```

4. DNS propagation bekle (5-30 dakika)

#### Frontend için:
1. Render Dashboard → `financeml-frontend` service
2. "Settings" → "Custom Domain"
3. "Add Custom Domain" → `yourdomain.me` veya `www.yourdomain.me`
4. DNS kayıtlarını domain'e ekle

### 4. SSL Sertifikası

Render otomatik olarak Let's Encrypt SSL sertifikası oluşturur. 
DNS ayarları tamamlandıktan sonra HTTPS otomatik aktif olur.

---

## 📊 Cache ve Data Yönetimi

### Problem: Render Free Tier Persistent Disk Yok

**Çözüm 1: GitHub'da Cache Dosyalarını Commit Et**
```bash
git add data/cache/
git commit -m "chore: Add cached market data"
git push origin main
```

**Çözüm 2: External Storage Kullan**
- AWS S3 (ücretsiz tier)
- Cloudflare R2 (ücretsiz 10GB)
- Google Cloud Storage

**Çözüm 3: Cache'i Deploy Sırasında Oluştur**
`render-start.sh` içinde:
```bash
python update_cache.py
```
⚠️ **Dikkat**: Her deploy'da cache yeniden oluşur (2-3 dakika ekstra süre)

---

## 🔧 Render Environment Variables

### API Servisi için:

```env
# Required
PYTHONUNBUFFERED=1
PORT=8000

# Optional
LOG_LEVEL=INFO
ALPHA_VANTAGE_API_KEY=your_key_here
POLYGON_API_KEY=your_key_here

# Database (opsiyonel)
DATABASE_URL=postgresql://...
```

### Frontend için:

```env
REACT_APP_API_URL=https://api.yourdomain.me
# veya
REACT_APP_API_URL=https://financeml-api.onrender.com
```

---

## 🚦 Health Check ve Monitoring

### API Health Check
Render otomatik olarak `/health` endpoint'ini kontrol eder.

### Logs
```bash
# Render Dashboard'dan
Services → financeml-api → Logs

# veya CLI ile
render logs -s financeml-api
```

### Metrics
Render Dashboard'da built-in metrics:
- Request count
- Response time
- Memory usage
- CPU usage

---

## 💡 Optimizasyon İpuçları

### 1. Cold Start Süresini Azalt
```python
# api/main.py içinde startup event
@app.on_event("startup")
async def startup_event():
    # Modelleri pre-load et
    pass
```

### 2. Free Tier Limitleri
- Her ay 750 saat ücretsiz
- 2 servis = 375 saat/servis = ~15.6 gün sürekli çalışma
- İhtiyaçtan fazlası için ücretli plan gerekir

### 3. Auto-Deploy
Her push'ta otomatik deploy:
```yaml
# render.yaml
autoDeploy: true
```

Manuel deploy için:
```bash
# Render Dashboard'dan "Manual Deploy" butonu
```

---

## 🔐 Güvenlik

### 1. Secrets Yönetimi
API keys'leri Environment Variables'a ekle, asla kod'a commit etme.

### 2. CORS Ayarları
`api/main.py` içinde production domain'i ekle:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://yourdomain.me",
        "https://www.yourdomain.me",
        "http://localhost:3000"  # development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate Limiting
Production'da rate limiting ekle:
```bash
pip install slowapi
```

---

## 📞 Domain Önerileri

İyi domain örnekleri:
- `financeml.me`
- `yourname-ml.me`
- `stockpredict.tech`
- `aifinance.tech`
- `mltrader.me`

Kısa, akılda kalıcı, proje ile ilgili olmalı.

---

## 🎯 Final Checklist

- [ ] GitHub repo public ve güncel
- [ ] `render.yaml` commit edildi
- [ ] Render account oluşturuldu
- [ ] API servisi deploy edildi ve `/health` çalışıyor
- [ ] Frontend deploy edildi ve API URL ayarlandı
- [ ] GitHub Student Pack aktif
- [ ] Domain satın alındı (ücretsiz)
- [ ] DNS kayıtları eklendi
- [ ] SSL sertifikası aktif (HTTPS)
- [ ] CORS ayarları production domain'i içeriyor

---

## 🆘 Troubleshooting

### Deploy Başarısız
```bash
# Render logs'a bak
# Build logs'ta hatayı bul
# Environment variables'ı kontrol et
```

### Cold Start Çok Yavaş
```bash
# Model dosyalarını küçült
# Lazy loading kullan
# Paid tier'a geç (instant spin-up)
```

### DNS Çalışmıyor
```bash
# DNS propagation kontrol
dig api.yourdomain.me

# Namecheap DNS ayarlarını kontrol et
# TTL'yi 60'a düşür (test için)
```

---

**Deployment başarıyla tamamlandığında projeniz şu URL'lerden erişilebilir olacak:**

- 🌐 Frontend: `https://yourdomain.me`
- 🔧 API: `https://api.yourdomain.me`
- 📊 Docs: `https://api.yourdomain.me/docs`

Başarılar! 🚀
