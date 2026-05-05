from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.affiliate_link import AffiliateLink
from app.models.content import Content
from app.models.performance import Performance
from app.models.product import Product
from app.schemas.content import ContentResponse
from app.schemas.performance import PerformanceStatusResponse
from app.services.content_service import ContentService
from app.services.decision_service import DecisionService
from app.services.export_service import ExportService
from app.services.insights_service import InsightsService
from app.services.winner_service import WinnerService

router = APIRouter(prefix="/content", tags=["Content"])
logger = logging.getLogger(__name__)


@router.post("/generate/{product_id}", response_model=list[ContentResponse], status_code=status.HTTP_201_CREATED)
async def generate_content_for_product(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> list[Content]:
    product = await db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    generated = await ContentService.generate_ai_content(product.name)

    rows: list[Content] = []
    for hook in generated["hooks"]:
        for script in generated["scripts"]:
            cta = generated["ctas"][len(rows) % len(generated["ctas"])]
            rows.append(
                Content(
                    product_id=product_id,
                    hook=hook,
                    script=script,
                    cta=cta,
                    status="draft",
                )
            )

    db.add_all(rows)
    await db.commit()

    for row in rows:
        await db.refresh(row)

    logger.info("content generated", extra={"product_id": product_id, "count": len(rows)})
    return rows


@router.get("/export/{content_id}")
async def export_content_for_platform(
    content_id: int,
    platform: str = "tiktok",
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, str]:
    content = await db.get(Content, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")

    link_result = await db.execute(
        select(AffiliateLink)
        .where(AffiliateLink.product_id == content.product_id)
        .order_by(AffiliateLink.created_at.desc())
        .limit(1)
    )
    affiliate_link = link_result.scalar_one_or_none()

    if affiliate_link is not None:
        logger.info(
            "link usage exported",
            extra={
                "content_id": content_id,
                "product_id": content.product_id,
                "tracking_code": affiliate_link.tracking_code,
                "platform": platform,
            },
        )

    return ExportService.format_for_platform(content, platform, affiliate_link)


@router.get("/performance-status/{content_id}", response_model=PerformanceStatusResponse)
async def get_content_performance_status(
    content_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> PerformanceStatusResponse:
    content = await db.get(Content, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")

    result = await db.execute(
        select(Performance)
        .where(Performance.content_id == content_id)
        .order_by(Performance.created_at.desc())
    )
    performance_entries = list(result.scalars().all())

    views = sum(item.views for item in performance_entries)
    likes = sum(item.likes for item in performance_entries)
    clicks = sum(item.clicks for item in performance_entries)
    conversions = sum(item.conversions for item in performance_entries)
    revenue = round(sum(item.revenue for item in performance_entries), 2)
    click_rate = round(clicks / views, 4) if views else 0.0
    conversion_rate = round(conversions / clicks, 4) if clicks else 0.0

    aggregate = Performance(
        content_id=content_id,
        platform="all",
        views=views,
        likes=likes,
        clicks=clicks,
        conversions=conversions,
        revenue=revenue,
    )

    return PerformanceStatusResponse(
        status=WinnerService.is_winner(aggregate),
        views=views,
        likes=likes,
        clicks=clicks,
        conversions=conversions,
        revenue=revenue,
        click_rate=click_rate,
        conversion_rate=conversion_rate,
    )


@router.get("/decision/{content_id}")
async def get_content_decision(
    content_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    content = await db.get(Content, content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")

    result = await db.execute(
        select(Performance)
        .where(Performance.content_id == content_id)
        .order_by(Performance.created_at.desc())
    )
    performance_entries = list(result.scalars().all())

    aggregate = Performance(
        content_id=content_id,
        platform="all",
        views=sum(item.views for item in performance_entries),
        likes=sum(item.likes for item in performance_entries),
        clicks=sum(item.clicks for item in performance_entries),
        conversions=sum(item.conversions for item in performance_entries),
        revenue=round(sum(item.revenue for item in performance_entries), 2),
    )
    insights = InsightsService.analyze_performance(aggregate)
    db.add(insights)
    await db.commit()
    await db.refresh(insights)

    action = DecisionService.decide_action(content, insights)

    return {
        "scores": {
            "hook_score": insights.hook_score,
            "engagement_score": insights.engagement_score,
            "conversion_score": insights.conversion_score,
            "overall_score": insights.overall_score,
        },
        "recommended_action": action,
    }


@router.get("/{product_id}", response_model=list[ContentResponse])
async def get_content_by_product(
    product_id: int,
    db: AsyncSession = Depends(get_db_session),
) -> list[Content]:
    result = await db.execute(
        select(Content)
        .where(Content.product_id == product_id)
        .order_by(Content.created_at.desc())
    )
    return list(result.scalars().all())
