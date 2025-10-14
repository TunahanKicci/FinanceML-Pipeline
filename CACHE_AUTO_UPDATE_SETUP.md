# Otomatik Cache Güncelleme Kurulumu

## Amaç
Her gün saat 18:00'de otomatik olarak Yahoo Finance'den veri çekerek cache'i güncel tutmak.

## Windows Task Scheduler Kurulumu

### Adım 1: Task Scheduler'ı Aç
```
Win + R → taskschd.msc → Enter
```

### Adım 2: Yeni Görev Oluştur
1. **Create Basic Task** → "FinanceML Daily Cache Update" 
2. **Trigger**: Daily, 18:00
3. **Action**: Start a program
   - **Program/script**: `powershell.exe`
   - **Arguments**: `-ExecutionPolicy Bypass -File "C:\proje\FinanceML-Pipeline\update_and_reload.ps1"`
   - **Start in**: `C:\proje\FinanceML-Pipeline`

### Adım 3: Ek Ayarlar
- **Run whether user is logged on or not**
- **Run with highest privileges**
- **Configure for: Windows 10/11**

## Manuel Test
```powershell
cd C:\proje\FinanceML-Pipeline
.\update_and_reload.ps1
```

## Docker Volume Mount Nasıl Çalışır?

### docker-compose.yml'de:
```yaml
volumes:
  - ./data:/app/data  # Local data klasörü → Docker container
```

Bu sayede:
1. Local'de `update_cache.py` çalıştırınca `data/cache/` güncellenir
2. Docker container aynı klasöre mount edildiği için **otomatik** görür
3. Container restart gerekmez! (Read-only access)

## Kontrol

### Cache Güncellenmiş mi?
```powershell
Get-ChildItem data/cache/*.csv | Select-Object Name, LastWriteTime
```

### Docker'da Cache Görülüyor mu?
```powershell
docker exec financeml_api ls -lh /app/data/cache/
```

## Zamanlama Önerileri

| Zamanlama | Neden |
|-----------|-------|
| **18:00** | US markets kapanışı (16:00 ET + 2 saat) |
| **09:00** | Sabah erken güncelleme (pre-market) |
| **00:00** | Gece yarısı batch job |

## Sorun Giderme

### Problem: Script çalışmıyor
```powershell
# Execution policy kontrolü
Get-ExecutionPolicy

# Geçici çözüm
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### Problem: Python bulunamıyor
```powershell
# Task Scheduler'da tam path kullan
"C:\Python310\python.exe" update_cache.py
```

### Problem: Docker container eskiyi kullanıyor
```powershell
# Cache'in timestamp'ini kontrol et
docker exec financeml_api stat /app/data/cache/AAPL_2y_1d.csv
```

## Monitoring

### Log Dosyası
Script output'u yakalamak için:
```powershell
# update_and_reload.ps1 içine ekle:
Start-Transcript -Path "logs/cache_update_$(Get-Date -Format 'yyyy-MM-dd').log"
# ... script ...
Stop-Transcript
```

## Avantajlar

1. **Sıfır Downtime**: Container restart yok
2. **Real-time**: Dosya güncellenince anında aktif
3. **Basit**: Ek konfigürasyon gerekmez
4. **Güvenli**: Read-only mount (container veriyi değiştiremiyor)

## İleri Seviye

### Farklı Cache Stratejileri

#### A. Intraday Updates (Gün içi)
```powershell
# Her 15 dakikada bir
# Task Scheduler → Trigger → Repeat task every 15 minutes
```

#### B. Market Saatlerine Göre
```powershell
# Sadece market açık olduğunda
if ((Get-Date).Hour -ge 9 -and (Get-Date).Hour -le 16) {
    python update_cache.py
}
```

#### C. Conditional Update
```powershell
# Sadece hafta içi
if ([int](Get-Date).DayOfWeek -ge 1 -and [int](Get-Date).DayOfWeek -le 5) {
    python update_cache.py
}
```

## Güvenlik

### API Key'leri Koruma
`.env` dosyasında sakla:
```env
ALPHA_VANTAGE_API_KEY=your_key
NEWS_API_KEY=your_key
```

Task Scheduler'da `.env` dosyası otomatik yüklenir (script'te tanımlı).

---

Artık cache'iniz her gün otomatik güncellenecek ve Docker anında kullanacak!
