# Monitoring Setup

Bu proje Prometheus ve Grafana kullanarak basit bir monitoring sistemi içerir.

## Servisler

### Prometheus (Port 9090)
- **URL**: http://localhost:9090
- **Amaç**: Metrik toplama ve depolama
- **Scrape Targets**:
  - FinanceML API (localhost:8000/metrics)
  - Prometheus self-monitoring
  - cAdvisor (container metrics)
  - Node Exporter (system metrics)

### Grafana (Port 3001)
- **URL**: http://localhost:3001
- **Default Credentials**:
  - Username: `admin`
  - Password: `admin`
- **Pre-configured Datasource**: Prometheus
- **Dashboards**: FinanceML API Dashboard

### cAdvisor (Port 8080)
- **URL**: http://localhost:8080
- **Amaç**: Container metrics (CPU, memory, network, disk)
- **Auto-scraped by Prometheus**

### Node Exporter (Port 9100)
- **URL**: http://localhost:9100
- **Amaç**: Host system metrics
- **Auto-scraped by Prometheus**

## Metriklr

### HTTP Metrics
- `http_requests_total`: Total HTTP requests by method, endpoint, and status
- `http_request_duration_seconds`: Request latency histogram

### Application Metrics
- `predictions_total`: Total predictions made by symbol and model
- `cache_hits_total`: Cache hit count by data type
- `cache_misses_total`: Cache miss count by data type

### System Metrics
- `cpu_usage_percent`: CPU usage percentage
- `memory_usage_percent`: Memory usage percentage
- `disk_usage_percent`: Disk usage percentage

## Kurulum

### 1. Docker Compose ile başlatma

```bash
# Tüm servisleri başlat
docker-compose up -d

# Sadece monitoring servislerini başlat
docker-compose up -d prometheus grafana cadvisor node-exporter
```

### 2. Prometheus'u kontrol et

http://localhost:9090 adresine git ve şu query'leri test et:

```promql
# Request rate
rate(http_requests_total[5m])

# P95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Cache hit rate
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

### 3. Grafana Dashboard'u aç

1. http://localhost:3001 adresine git
2. admin/admin ile giriş yap (ilk girişte şifre değiştirmeyi iste)
3. Sol menüden "Dashboards" → "FinanceML API Dashboard" seç

## Dashboard Panelleri

### HTTP Request Rate
- Son 5 dakikadaki request rate grafiği
- Method ve endpoint breakdown

### CPU Usage
- Gerçek zamanlı CPU kullanımı gauge
- Eşik değerleri: >50% sarı, >75% kırmızı

### Memory Usage
- Gerçek zamanlı memory kullanımı gauge
- Eşik değerleri: >70% sarı, >85% kırmızı

### Prediction Rate
- Model prediction rate'i
- Symbol ve model type breakdown

### Cache Hit/Miss Rate
- Cache performansı
- Yeşil: hits, Kırmızı: misses

### Response Time (P95/P99)
- 95th ve 99th percentile response time
- Endpoint breakdown

## Alert Kuralları (Opsiyonel)

Prometheus alertmanager eklemek için `monitoring/prometheus/alerts.yml` oluştur:

```yaml
groups:
  - name: financeml_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} requests/sec"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P95 latency is {{ $value }}s"
      
      - alert: LowCacheHitRate
        expr: rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m])) < 0.8
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value }}"
```

## Troubleshooting

### Metrics endpoint'e erişilemiyor

```bash
# API container'a gir
docker exec -it financeml_api bash

# Metrics endpoint'i test et
curl http://localhost:8000/metrics
```

### Prometheus targets "down"

```bash
# Prometheus logs
docker logs financeml_prometheus

# Network bağlantısını kontrol et
docker network inspect financeml-pipeline_finance_network
```

### Grafana dashboard boş

1. Grafana'da Settings → Data Sources'a git
2. Prometheus datasource'u test et
3. Dashboard'da query'leri manuel çalıştır

## Production Deployment

Production'da şunları düşün:

1. **Security**: 
   - Grafana admin şifresini değiştir
   - Prometheus ve Grafana'yı authentication arkasına al
   - Metrics endpoint'i internal network'e kısıtla

2. **Persistence**:
   - Prometheus ve Grafana data volume'leri backup al
   - Retention policy ayarla (default 15 days)

3. **Alerting**:
   - Alertmanager ekle
   - Slack/Email/PagerDuty integration

4. **Scaling**:
   - Prometheus remote storage (Thanos, Cortex)
   - Grafana clustering

## Kaynaklar

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [FastAPI Prometheus](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [cAdvisor](https://github.com/google/cadvisor)
