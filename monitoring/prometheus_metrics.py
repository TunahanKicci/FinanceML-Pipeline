# monitoring/prometheus_metrics.py
"""
Prometheus metrics for FastAPI application
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from fastapi import Response
import time
import psutil

# HTTP Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# API specific metrics
predictions_total = Counter(
    'predictions_total',
    'Total number of predictions made',
    ['symbol', 'model']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_type']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_type']
)

# System metrics
cpu_usage = Gauge('cpu_usage_percent', 'CPU usage percentage')
memory_usage = Gauge('memory_usage_percent', 'Memory usage percentage')
disk_usage = Gauge('disk_usage_percent', 'Disk usage percentage')

# Active connections
active_requests = Gauge('active_requests', 'Number of active requests')


def update_system_metrics():
    """Update system metrics"""
    try:
        cpu_usage.set(psutil.cpu_percent(interval=1))
        memory_usage.set(psutil.virtual_memory().percent)
        disk_usage.set(psutil.disk_usage('/').percent)
    except Exception as e:
        print(f"Error updating system metrics: {e}")


def get_metrics():
    """Generate Prometheus metrics"""
    update_system_metrics()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
