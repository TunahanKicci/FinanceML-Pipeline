# 🚀 FinanceML Pipeline - Deployment Checklist

Bu checklist'i kullanarak Render'da deployment ve GitHub Student Pack ile domain alımını adım adım tamamlayın.

---

## 📋 Ön Hazırlık

### ✅ Repository Hazırlığı
- [ ] GitHub repository public ve güncel
- [ ] Tüm dosyalar commit edildi
- [ ] `render.yaml` dosyası mevcut
- [ ] `render-start.sh` dosyası mevcut
- [ ] `.gitignore` dosyası düzgün yapılandırılmış
- [ ] Cache dosyaları commit edildi veya deploy sırasında oluşturulacak

```bash
git status
git add .
git commit -m "feat: Add Render deployment configuration"
git push origin main
```

---

## 🏗️ Render Deployment

### 1. Render Account
- [ ] https://render.com adresine git
- [ ] "Sign up with GitHub" ile kayıt ol
- [ ] GitHub repository'lerine erişim izni ver

### 2. Backend API Deploy (Blueprint Yöntemi - Önerilen)

- [ ] Render Dashboard → "New +" → "Blueprint"
- [ ] Repository seç: `TunahanKicci/FinanceML-Pipeline`
- [ ] `render.yaml` otomatik algılandı ✓
- [ ] "Apply" butonuna tıkla
- [ ] Deploy başladı - logs'u izle (10-15 dakika)

**Environment Variables (Otomatik ayarlanacak):**
- [ ] `PYTHONUNBUFFERED=1`
- [ ] `LOG_LEVEL=INFO`
- [ ] `PORT=8000`
- [ ] `ENVIRONMENT=production` (opsiyonel)

### 3. Frontend Deploy (Blueprint ile otomatik)

Blueprint kullanıldığında otomatik oluşturulur:
- [ ] Frontend servisi oluşturuldu
- [ ] Build command doğru: `npm install --legacy-peer-deps && npm run build`
- [ ] Publish directory: `build`

**Environment Variables:**
- [ ] `REACT_APP_API_URL` → API URL'inizle güncelleyin

**Manuel Güncelleme Gerekiyorsa:**
```
1. Render Dashboard → financeml-frontend
2. Settings → Environment
3. Add Environment Variable:
   Key: REACT_APP_API_URL
   Value: https://financeml-api-XXXXX.onrender.com
```

### 4. Deploy Sonrası Test

**API Test:**
- [ ] `https://financeml-api-XXXXX.onrender.com/health` açılıyor
- [ ] `https://financeml-api-XXXXX.onrender.com/docs` Swagger UI görünüyor
- [ ] `https://financeml-api-XXXXX.onrender.com/metrics` Prometheus metrics görünüyor

```bash
# PowerShell
Invoke-WebRequest -Uri "https://your-api.onrender.com/health"
```

**Frontend Test:**
- [ ] `https://financeml-frontend-XXXXX.onrender.com` açılıyor
- [ ] UI yükleniyor
- [ ] API bağlantısı çalışıyor (Network tab kontrol)

---

## 🎓 GitHub Student Pack ile Domain

### 1. GitHub Student Pack Aktivasyon

- [ ] https://education.github.com/pack adresine git
- [ ] "Get the Pack" butonuna tıkla
- [ ] Öğrenci kimliği belgesi yükle (öğrenci kartı, transkript)
- [ ] Okul email adresi (.edu.tr veya öğrenci maili)
- [ ] Başvuru gönderildi
- [ ] Onay bekleniyor (1-3 iş günü)
- [ ] ✅ Student Pack aktif

### 2. Domain Satın Alma (Namecheap - Önerilen)

**Student Pack aktif olduktan sonra:**

- [ ] https://nc.me adresine git
- [ ] GitHub ile giriş yap
- [ ] Student discount aktif olduğundan emin ol

**Domain Arama:**
- [ ] Domain adı belirle (örnekler):
  - `financeml.me`
  - `[isminiz]-ml.me`
  - `stockpredict.tech`
  - `aifinance.tech`

- [ ] Domain müsaitliği kontrol et
- [ ] 1 yıl ücretsiz .me domain seç
- [ ] "Add to cart" → Checkout
- [ ] Ödeme bilgileri (kredi kartı gerekli ama 1 yıl ücretsiz)
- [ ] Domain satın alındı ✓

**Alternatif: .tech Domain**
- [ ] https://get.tech/github-student-developer-pack adresine git
- [ ] 1 yıl ücretsiz .tech domain al
- [ ] Aynı adımları takip et

---

## 🌐 Domain'i Render'a Bağlama

### 1. API Domain Ayarları

**Render'da:**
- [ ] Dashboard → `financeml-api` service
- [ ] "Settings" → "Custom Domain"
- [ ] "Add Custom Domain" tıkla
- [ ] Domain gir: `api.yourdomain.me`
- [ ] DNS kayıtlarını kopyala:
  ```
  Type: CNAME
  Name: api
  Value: financeml-api-XXXXX.onrender.com
  ```

**Namecheap'te:**
- [ ] Namecheap Dashboard → Domain List → Manage
- [ ] "Advanced DNS" sekmesi
- [ ] "Add New Record" tıkla
- [ ] CNAME kaydı ekle:
  - Type: `CNAME Record`
  - Host: `api`
  - Value: `financeml-api-XXXXX.onrender.com`
  - TTL: `Automatic`
- [ ] "Save All Changes"

### 2. Frontend Domain Ayarları

**Render'da:**
- [ ] Dashboard → `financeml-frontend` service
- [ ] "Settings" → "Custom Domain"
- [ ] "Add Custom Domain" tıkla
- [ ] Domain gir: `yourdomain.me` (apex domain)
- [ ] DNS kayıtlarını kopyala

**Namecheap'te:**
- [ ] "Advanced DNS" sekmesi
- [ ] CNAME kayıtları ekle:

**Root domain (@):**
```
Type: CNAME Record
Host: @
Value: financeml-frontend-XXXXX.onrender.com
TTL: Automatic
```

**WWW subdomain:**
```
Type: CNAME Record
Host: www
Value: financeml-frontend-XXXXX.onrender.com
TTL: Automatic
```

- [ ] "Save All Changes"

### 3. DNS Propagation Bekle

- [ ] 5-30 dakika bekle
- [ ] DNS propagation kontrol: https://dnschecker.org
- [ ] Domain'i test et: `https://yourdomain.me`
- [ ] API subdomain test: `https://api.yourdomain.me/health`

---

## 🔒 SSL Sertifikası

- [ ] Render otomatik SSL sertifikası oluşturdu (Let's Encrypt)
- [ ] HTTPS aktif: `https://yourdomain.me`
- [ ] HTTPS aktif: `https://api.yourdomain.me`
- [ ] Tarayıcıda kilit ikonu görünüyor ✓

---

## 🔧 Production Ayarları

### Frontend Environment Update

Frontend'in API URL'ini custom domain'e güncelle:

- [ ] Render Dashboard → `financeml-frontend`
- [ ] Settings → Environment
- [ ] `REACT_APP_API_URL` değiştir:
  ```
  Eski: https://financeml-api-XXXXX.onrender.com
  Yeni: https://api.yourdomain.me
  ```
- [ ] "Save Changes"
- [ ] Frontend otomatik redeploy olacak

### CORS Ayarları Update

`api/main.py` dosyasında custom domain'i ekle:

```python
allowed_origins = [
    "http://localhost:3000",
    "https://*.onrender.com",
    "https://yourdomain.me",      # Ekle
    "https://www.yourdomain.me",  # Ekle
    "https://api.yourdomain.me",  # Ekle
]
```

- [ ] Değişiklikleri commit et
- [ ] GitHub'a push et
- [ ] Render otomatik redeploy yapacak

```bash
git add api/main.py
git commit -m "feat: Add custom domain to CORS"
git push origin main
```

---

## ✅ Final Test

### API Endpoints
- [ ] `https://api.yourdomain.me/health` → `{"status": "healthy"}`
- [ ] `https://api.yourdomain.me/docs` → Swagger UI açılıyor
- [ ] `https://api.yourdomain.me/financials/AAPL` → JSON response

### Frontend
- [ ] `https://yourdomain.me` → Ana sayfa yükleniyor
- [ ] `https://www.yourdomain.me` → Redirect çalışıyor
- [ ] Stock prediction çalışıyor
- [ ] Charts render oluyor
- [ ] API bağlantısı stabil

### Security
- [ ] HTTPS zorunlu (HTTP redirect)
- [ ] SSL sertifikası geçerli
- [ ] CORS ayarları doğru
- [ ] API keys environment variables'da

---

## 📊 Monitoring

### Render Dashboard
- [ ] API service "Running" durumda
- [ ] Frontend service "Running" durumda
- [ ] Build logs kontrol edildi
- [ ] Deploy logs kontrol edildi

### Performance
- [ ] Cold start süresi test edildi (~10-30 saniye)
- [ ] Response time kabul edilebilir (<2 saniye)
- [ ] Memory usage stabil

---

## 🎉 Deployment Tamamlandı!

**Live URLs:**
- 🌐 **Frontend**: `https://yourdomain.me`
- 🔧 **API**: `https://api.yourdomain.me`
- 📚 **Docs**: `https://api.yourdomain.me/docs`

**GitHub Repository:**
- 📦 **Repo**: `https://github.com/TunahanKicci/FinanceML-Pipeline`

**Social Media için:**
```
🚀 FinanceML Pipeline deployed!

AI-powered stock prediction & portfolio optimization
- LSTM price forecasting
- Real-time risk analysis
- Portfolio optimization
- Sentiment analysis

🔗 Try it: https://yourdomain.me
💻 GitHub: https://github.com/TunahanKicci/FinanceML-Pipeline

#MachineLearning #FinTech #AI #Python #React #Finance
```

---

## 🆘 Troubleshooting

### Deploy Failed
- [ ] Logs'u kontrol et: Render Dashboard → Logs
- [ ] Build errors var mı?
- [ ] Environment variables doğru mu?
- [ ] Dockerfile path doğru mu?

### Domain Çalışmıyor
- [ ] DNS kayıtları doğru mu?
- [ ] DNS propagation tamamlandı mı? (dnschecker.org)
- [ ] CNAME değerleri doğru mu?
- [ ] TTL çok yüksek değil mi? (60 olarak ayarla)

### API Slow/Not Responding
- [ ] Cold start mı? (15 dk inactivity sonrası)
- [ ] Logs'ta error var mı?
- [ ] Health check endpoint çalışıyor mu?

### CORS Errors
- [ ] Frontend domain CORS listesinde mi?
- [ ] `allowed_origins` güncellendi mi?
- [ ] Redeploy yapıldı mı?

---

**Not**: Bu checklist'i yazdıkça ilerleyin. Her ✅ işaretlediğinizde bir adım daha yaklaşıyorsunuz! 🎯
