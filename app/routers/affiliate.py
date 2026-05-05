from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.affiliate_link import AffiliateLink
from app.models.product import Product
from app.schemas.affiliate import AffiliateLinkCreate, AffiliateLinkResponse
from app.services.link_tracking_service import LinkTrackingService

router = APIRouter(prefix="/affiliate", tags=["Affiliate"])
logger = logging.getLogger(__name__)


@router.post("/create", response_model=AffiliateLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_affiliate_link(
    payload: AffiliateLinkCreate,
    db: AsyncSession = Depends(get_db_session),
) -> AffiliateLink:
    product = await db.get(Product, payload.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    tracking_data = LinkTrackingService.generate_tracking_link(
        payload.product_id,
        payload.original_url,
    )
    affiliate_link = AffiliateLink(
        product_id=payload.product_id,
        original_url=tracking_data["original_url"],
        tracking_code=tracking_data["tracking_code"],
        landing_page_url=tracking_data["landing_page_url"],
    )

    db.add(affiliate_link)
    await db.commit()
    await db.refresh(affiliate_link)

    logger.info(
        "link usage created",
        extra={"product_id": payload.product_id, "tracking_code": affiliate_link.tracking_code},
    )
    return affiliate_link


@router.get("/{product_id}", response_model=list[AffiliateLinkResponse])
async def get_affiliate_links(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> list[AffiliateLink]:
    result = await db.execute(
        select(AffiliateLink)
        .where(AffiliateLink.product_id == product_id)
        .order_by(AffiliateLink.created_at.desc())
    )
    return list(result.scalars().all())
