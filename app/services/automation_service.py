from __future__ import annotations

import logging
import random

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.product import Product
from app.models.trend import Trend
from app.services.content_service import ContentService
from app.services.scoring_service import ScoringService
from app.services.scaling_service import ScalingService
from app.services.trend_service import TrendService

logger = logging.getLogger(__name__)


class AutomationService:
    @staticmethod
    async def run_cycle(db: AsyncSession) -> dict[str, int]:
        trend_payloads = await TrendService.fetch_trends()
        qualified_trends = [trend for trend in trend_payloads if trend.trend_score > 70]

        trend_rows = [Trend(**trend.model_dump()) for trend in qualified_trends]
        db.add_all(trend_rows)
        await db.flush()
        logger.info("trends fetched", extra={"count": len(trend_rows)})

        product_rows: list[Product] = []
        for trend in trend_rows:
            commission = round(random.uniform(15, 45), 2)
            virality_score = random.uniform(50, 100)
            profit_score = ScoringService.calculate_profit_score(
                trend_score=trend.trend_score,
                commission=commission,
                virality_score=virality_score,
            )
            product_rows.append(
                Product(
                    name=f"{trend.keyword.title()} Affiliate Offer",
                    source="automation",
                    price=round(random.uniform(19, 199), 2),
                    commission=commission,
                    trend_id=trend.id,
                    profit_score=profit_score,
                )
            )

        db.add_all(product_rows)
        await db.flush()
        logger.info("products created", extra={"count": len(product_rows)})

        content_rows: list[Content] = []
        for product in product_rows:
            generated = await ContentService.generate_ai_content(product.name)
            for hook in generated["hooks"]:
                for script in generated["scripts"]:
                    cta = generated["ctas"][len(content_rows) % len(generated["ctas"])]
                    content_rows.append(
                        Content(
                            product_id=product.id,
                            hook=hook,
                            script=script,
                            cta=cta,
                            status="draft",
                        )
                    )

        db.add_all(content_rows)
        await db.commit()
        logger.info("content generated", extra={"count": len(content_rows)})
        scaling_result = await ScalingService.process_scaling(db)

        return {
            "trends_fetched": len(trend_payloads),
            "trends_qualified": len(trend_rows),
            "products_created": len(product_rows),
            "content_generated": len(content_rows),
            "winners_detected": scaling_result["winners_detected"],
            "variations_generated": scaling_result["variations_generated"],
            "queue_size": scaling_result["queue_size"],
        }
