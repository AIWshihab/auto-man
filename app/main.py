from __future__ import annotations

import logging

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import Base, engine
from app.routers.affiliate import router as affiliate_router
from app.routers.analytics import router as analytics_router
from app.routers.automation import router as automation_router
from app.routers.content import router as content_router
from app.routers.performance import router as performance_router
from app.routers.products import router as products_router
from app.routers.scaling import router as scaling_router
from app.routers.tracking import router as tracking_router
from app.routers.trends import router as trends_router

app = FastAPI(title=settings.app_name, version=settings.app_version)
logger = logging.getLogger(__name__)


@app.on_event("startup")
async def on_startup() -> None:
    print("Server starting...")
    async with engine.begin() as conn:
        print("DB connected")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Startup complete")


app.include_router(trends_router)
app.include_router(products_router)
app.include_router(content_router)
app.include_router(automation_router)
app.include_router(performance_router)
app.include_router(scaling_router)
app.include_router(affiliate_router)
app.include_router(tracking_router)
app.include_router(analytics_router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
