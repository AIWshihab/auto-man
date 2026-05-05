from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.trend import Trend
from app.schemas.trend import TrendResponse
from app.services.trend_service import TrendService

router = APIRouter(prefix="/trends", tags=["Trends"])
logger = logging.getLogger(__name__)


@router.post("/fetch", response_model=list[TrendResponse])
async def fetch_trends(db: AsyncSession = Depends(get_db_session)) -> list[Trend]:
    trend_payloads = await TrendService.fetch_trends()
    trend_rows = [Trend(**trend.model_dump()) for trend in trend_payloads]

    db.add_all(trend_rows)
    await db.commit()

    for row in trend_rows:
        await db.refresh(row)

    logger.info("trends fetched", extra={"count": len(trend_rows)})
    return trend_rows


@router.get("", response_model=list[TrendResponse])
async def list_trends(db: AsyncSession = Depends(get_db_session)) -> list[Trend]:
    result = await db.execute(select(Trend).order_by(Trend.created_at.desc()))
    return list(result.scalars().all())
