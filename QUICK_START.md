# FinanceML Pipeline - Quick Start Guide

## Hızlı Başlangıç

### 1. Cache'i Güncelle (Opsiyonel ama önerili)

```powershell
python update_cache.py
```

Bu komut:
- 10 hisse senedi için güncel fiyat verilerini indirir (AAPL, MSFT, GOOGL, vb.)
- S&P 500 endeks verilerini çeker
- Fundamental verileri günceller
- Her şeyi `data/cache/` dizinine kaydeder

**Süre**: ~2-3 dakika

### 2. Docker Container'ları Başlat

```powershell
docker-compose up -d --build
```

Bu komut:
- API container'ı (FastAPI backend) - Port 8000
- Frontend container'ı (React UI) - Port 3000
- Prometheus (Monitoring) - Port 9090
- Grafana (Dashboards) - Port 3001
- cAdvisor (Container metrics) - Port 8080

**İlk build**: ~5-8 dakika
**Sonraki başlatmalar**: ~30 saniye

### 3. Servislerin Durumunu Kontrol Et

```powershell
docker ps
```

Tüm container'lar "Up" ve "healthy" statüsünde olmalı.

## Servislere Erişim

### Frontend (Web UI)
```
http://localhost:3000
```
- React tabanlı modern arayüz
- Gerçek zamanlı tahminler
- Portfolio optimizasyonu
- Risk analizi

### API (Backend)
```
http://localhost:8000
```
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

### Prometheus (Metrics)
```
http://localhost:9090
```
- Metrik toplama ve sorgulama
- Query örnekleri için `docs/MONITORING.md`

### Grafana (Dashboards)
```
http://localhost:3001
```
- **Username**: admin
- **Password**: admin
- Pre-configured dashboard: "FinanceML API Dashboard"

### cAdvisor (Container Stats)
```
http://localhost:8080
```
- Container CPU, memory, network metrikleri

## API Endpoint'leri

### 1. Financial Metrics (Temel Analiz)
```powershell
# PowerShell
Invoke-WebRequest -Uri "http://localhost:8000/financials/AAPL" | Select-Object -Expand Content | ConvertFrom-Json

# veya
curl http://localhost:8000/financials/AAPL
```

**Response**: P/E ratio, ROE, profit margin, debt, vb.

### 2. Risk Analysis (Risk Analizi)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/risk/AAPL" | Select-Object -Expand Content | ConvertFrom-Json
```

**Response**: VaR, CVaR, Sharpe ratio, volatility, max drawdown

### 3. Price Forecast (LSTM Tahmin)
```powershell
$body = @{
    symbol = "AAPL"
    days = 30
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/forecast" -Method POST -Body $body -ContentType "application/json" | Select-Object -Expand Content | ConvertFrom-Json
```

**Response**: 30 günlük fiyat tahmini

### 4. Portfolio Optimization (Portföy Optimizasyonu)
```powershell
$body = @{
    symbols = @("AAPL", "MSFT", "GOOGL")
    risk_tolerance = "moderate"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/portfolio/optimize" -Method POST -Body $body -ContentType "application/json" | Select-Object -Expand Content | ConvertFrom-Json
```

**Response**: Optimal ağırlıklar, beklenen getiri, risk

### 5. Sentiment Analysis (Haber Duygu Analizi)
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/sentiment/AAPL" | Select-Object -Expand Content | ConvertFrom-Json
```

**Response**: Pozitif/negatif/nötr haber analizi

## Servisleri Durdur

```powershell
docker-compose down
```

Volume'leri de silmek için (tüm verileri temizler):
```powershell
docker-compose down -v
```

## Cache'i Otomatik Güncelleme

Cache her 24 saatte bir otomatik güncellenir (GitHub Actions).

Manuel güncellemek için:
```powershell
python update_cache.py
```

## Monitoring Query Örnekleri

Prometheus'ta (http://localhost:9090) şu query'leri deneyin:

```promql
# Request rate (son 5 dakika)
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))

# API endpoint breakdown
sum by (endpoint) (rate(http_requests_total[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[5m])
```

## Troubleshooting

### Container başlamıyor
```powershell
# Logs'a bak
docker-compose logs api

# Yeniden başlat
docker-compose restart api
```

### Port zaten kullanımda
```powershell
# Port'u kullanan process'i bul
netstat -ano | findstr :8000

# Process'i durdur (TaskID ile)
taskkill /PID <PID> /F
```

### Cache güncel değil
```powershell
# Cache'i yeniden oluştur
python update_cache.py

# Docker volume'ü yeniden mount et
docker-compose down
docker-compose up -d
```

### API yavaş çalışıyor
- Cache dosyalarının var olduğunu kontrol et: `data/cache/`
- Prometheus'ta latency'e bak: http://localhost:9090
- API logs: `docker-compose logs api`

## Detaylı Dokümantasyon

- **Monitoring**: `docs/MONITORING.md`
- **API Endpoints**: http://localhost:8000/docs
- **CI/CD Pipeline**: `.github/workflows/`
- **Architecture**: `README.md`

## Sonraki Adımlar

1. Servisleri başlat
2. Frontend'i aç (http://localhost:3000)
3. API'yi test et (http://localhost:8000/docs)
4. Grafana dashboard'u incele (http://localhost:3001)
5. Prometheus query'leri dene (http://localhost:9090)

## Tips

- Cache güncellemesi sabah piyasa açılmadan yapılmalı
- API container'ı ilk başlatmada model yüklediği için 30-40 saniye alır
- Prometheus verileri 15 gün saklanır (varsayılan)
- Grafana dashboard'ları `/monitoring/grafana/dashboards/` altında
- API rate limiting yok, production'da eklenmeli

---

Başarılı bir başlangıç için tüm adımları sırayla takip edin!
