from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.affiliate_link import AffiliateLink
from app.models.click_event import ClickEvent
from app.models.content import Content

router = APIRouter(tags=["Tracking"])
logger = logging.getLogger(__name__)


@router.get("/track/{tracking_code}")
async def track_click(
    tracking_code: str,
    content_id: int | None = Query(default=None),
    platform: str = Query(default="unknown"),
    db: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    result = await db.execute(
        select(AffiliateLink).where(AffiliateLink.tracking_code == tracking_code)
    )
    affiliate_link = result.scalar_one_or_none()
    if affiliate_link is None:
        raise HTTPException(status_code=404, detail="Tracking code not found")

    if content_id is not None:
        content = await db.get(Content, content_id)
        if content is None:
            content_id = None

    click_event = ClickEvent(
        content_id=content_id,
        affiliate_link_id=affiliate_link.id,
        platform=platform,
    )
    db.add(click_event)
    await db.commit()

    logger.info(
        "click logged",
        extra={
            "tracking_code": tracking_code,
            "affiliate_link_id": affiliate_link.id,
            "content_id": content_id,
            "platform": platform,
        },
    )
    return RedirectResponse(url=affiliate_link.original_url, status_code=307)
