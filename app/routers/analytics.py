from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.affiliate_link import AffiliateLink
from app.models.click_event import ClickEvent
from app.models.content import Content
from app.models.performance import Performance
from app.models.product import Product
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_analytics_summary(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    total_clicks_result = await db.execute(select(func.count()).select_from(ClickEvent))
    total_clicks = int(total_clicks_result.scalar_one())

    clicks_per_product_result = await db.execute(
        select(AffiliateLink.product_id, func.count(ClickEvent.id))
        .select_from(ClickEvent)
        .join(AffiliateLink, AffiliateLink.id == ClickEvent.affiliate_link_id)
        .group_by(AffiliateLink.product_id)
        .order_by(AffiliateLink.product_id)
    )
    clicks_per_product = {
        str(product_id): int(clicks)
        for product_id, clicks in clicks_per_product_result.all()
    }

    clicks_per_platform_result = await db.execute(
        select(ClickEvent.platform, func.count(ClickEvent.id))
        .group_by(ClickEvent.platform)
        .order_by(ClickEvent.platform)
    )
    clicks_per_platform = {
        platform: int(clicks)
        for platform, clicks in clicks_per_platform_result.all()
    }

    return {
        "total_clicks": total_clicks,
        "clicks_per_product": clicks_per_product,
        "clicks_per_platform": clicks_per_platform,
    }


@router.get("/report")
async def get_analytics_report(
    db: AsyncSession = Depends(get_db_session),
) -> dict[str, object]:
    performance_result = await db.execute(
        select(
            Content,
            func.coalesce(func.sum(Performance.views), 0).label("views"),
            func.coalesce(func.sum(Performance.likes), 0).label("likes"),
            func.coalesce(func.sum(Performance.clicks), 0).label("clicks"),
            func.coalesce(func.sum(Performance.conversions), 0).label("conversions"),
            func.coalesce(func.sum(Performance.revenue), 0).label("revenue"),
        )
        .join(Performance, Performance.content_id == Content.id)
        .group_by(Content.id)
    )

    content_scores: list[dict[str, object]] = []
    total_revenue = 0.0
    total_clicks = 0
    total_conversions = 0

    for content, views, likes, clicks, conversions, revenue in performance_result.all():
        aggregate = Performance(
            content_id=content.id,
            platform="all",
            views=int(views),
            likes=int(likes),
            clicks=int(clicks),
            conversions=int(conversions),
            revenue=float(revenue),
        )
        insights = InsightsService.analyze_performance(aggregate)
        total_revenue += float(revenue)
        total_clicks += int(clicks)
        total_conversions += int(conversions)
        content_scores.append(
            {
                "content_id": content.id,
                "product_id": content.product_id,
                "hook": content.hook,
                "overall_score": insights.overall_score,
                "views": int(views),
                "clicks": int(clicks),
                "conversions": int(conversions),
                "revenue": round(float(revenue), 2),
            }
        )

    top_contents = sorted(
        content_scores,
        key=lambda item: float(item["overall_score"]),
        reverse=True,
    )[:5]
    worst_contents = sorted(
        content_scores,
        key=lambda item: float(item["overall_score"]),
    )[:5]

    best_products_result = await db.execute(
        select(
            Product.id,
            Product.name,
            func.coalesce(func.sum(Performance.revenue), 0).label("revenue"),
            func.coalesce(func.sum(Performance.conversions), 0).label("conversions"),
        )
        .join(Content, Content.product_id == Product.id)
        .join(Performance, Performance.content_id == Content.id)
        .group_by(Product.id)
        .order_by(func.coalesce(func.sum(Performance.revenue), 0).desc())
        .limit(5)
    )
    best_products = [
        {
            "product_id": product_id,
            "name": name,
            "revenue": round(float(revenue), 2),
            "conversions": int(conversions),
        }
        for product_id, name, revenue, conversions in best_products_result.all()
    ]

    return {
        "top_5_performing_contents": top_contents,
        "worst_5_contents": worst_contents,
        "best_products": best_products,
        "total_revenue": round(total_revenue, 2),
        "conversion_rates": {
            "overall": round(total_conversions / total_clicks, 4) if total_clicks else 0.0,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
        },
    }
