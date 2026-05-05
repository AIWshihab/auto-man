from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.content import Content
from app.models.performance import Performance
from app.schemas.performance import PerformanceCreate, PerformanceResponse

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.post("/log", response_model=PerformanceResponse, status_code=status.HTTP_201_CREATED)
async def log_performance(
    payload: PerformanceCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Performance:
    content = await db.get(Content, payload.content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")

    performance = Performance(**payload.model_dump())
    db.add(performance)
    await db.commit()
    await db.refresh(performance)

    return performance


@router.get("/{content_id}", response_model=list[PerformanceResponse])
async def get_performance_by_content(
    content_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> list[Performance]:
    result = await db.execute(
        select(Performance)
        .where(Performance.content_id == content_id)
        .order_by(Performance.created_at.desc())
    )
    return list(result.scalars().all())
