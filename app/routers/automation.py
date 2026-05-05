from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/automation", tags=["Automation"])


@router.post("/run")
async def run_automation_cycle(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, int]:
    return await AutomationService.run_cycle(db)
