from fastapi import FastAPI

from app.routes.checkout import router as checkout_router
from app.routes.health import router as health_router

app = FastAPI(title="Payments API Demo", version="0.1.0")

app.include_router(health_router)
app.include_router(checkout_router)
