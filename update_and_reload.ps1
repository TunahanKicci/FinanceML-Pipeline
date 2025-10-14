# FinanceML Cache Update and Docker Reload Script
# Bu script günlük çalıştırılmalı (Windows Task Scheduler ile)

Write-Host " Starting FinanceML Cache Update..." -ForegroundColor Cyan

# 1. Cache'i güncelle
Write-Host "`n Updating cache data..." -ForegroundColor Yellow
python update_cache.py

if ($LASTEXITCODE -eq 0) {
    Write-Host " Cache updated successfully!" -ForegroundColor Green
    
    # 2. Docker container'ları yeniden başlat (cache volume mount sayesinde otomatik güncellenecek)
    # Gereksiz - Volume mount sayesinde otomatik yansıyor!
    Write-Host "`n Docker containers automatically see new cache data via volume mount!" -ForegroundColor Green
    Write-Host "No restart needed - containers will use updated cache on next request." -ForegroundColor Green
    
} else {
    Write-Host " Cache update failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n Update complete!" -ForegroundColor Cyan
