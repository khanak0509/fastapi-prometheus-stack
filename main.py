from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.routers import users, orders, products
from app.middleware import PrometheusMiddleware
from app.metrics import APP_INFO

app = FastAPI(
    title="E-Commerce API with Observability",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware to track request/response metrics
app.add_middleware(PrometheusMiddleware)

# API routes
app.include_router(users.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # Setting an info gauge so we know which version is running
    APP_INFO.labels(version="1.0.0", environment="production", service="ecommerce-api").set(1)

@app.get("/metrics")
async def metrics():
    # Exposing the endpoint that Prometheus will scrape
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health():
    # Basic health check for Docker/Kubernetes
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
