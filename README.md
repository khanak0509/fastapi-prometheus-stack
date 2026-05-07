# FastAPI + Prometheus Observability Stack

A production-ready boilerplate for building observable FastAPI applications. This project simulates a simple E-Commerce API and includes a full monitoring stack with automated metrics, alerting, and dashboards.

## Quick Start

Ensure you have **Docker** and **Docker Compose** installed, then run:

```bash
docker-compose up --build
```

## 🛠 Services

| Service              | URL                               | Description                     |
| -------------------- | --------------------------------- | ------------------------------- |
| **API**        | `http://localhost:8000`         | FastAPI Backend                 |
| **Metrics**    | `http://localhost:8000/metrics` | Raw Prometheus Metrics          |
| **Prometheus** | `http://localhost:9090`         | Time-series DB & Alerting       |
| **Grafana**    | `http://localhost:3000`         | Dashboards (Login: admin/admin) |

## Load Testing

To see the metrics and alerts in action, run the traffic generator:

```bash
python load_test.py
```

## Observability Features

- **Path Normalization**: Automatically groups paths like `/users/123` into `/users/{user_id}` for clean metrics.
- **DB Tracking**: Custom context manager for monitoring database operation latency.
- **Alerting**: Pre-configured rules for High Latency (P95 > 1s) and Error Rates (> 5%).
- **Provisioning**: Grafana is auto-configured to connect to Prometheus on startup.
