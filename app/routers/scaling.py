from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.scaling_service import ScalingService

router = APIRouter(prefix="/scaling", tags=["Scaling"])


@router.post("/run")
async def run_scaling(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    return await ScalingService.process_scaling(db)
