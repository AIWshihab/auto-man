from __future__ import annotations

import logging
import random

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.content import Content
from app.models.content_variant import ContentVariant
from app.models.performance import Performance
from app.models.scaling_queue import ScalingQueue
from app.services.decision_service import DecisionService
from app.services.insights_service import InsightsService

logger = logging.getLogger(__name__)


class ScalingService:
    @staticmethod
    async def generate_variations(
        content: Content,
        count: int | None = None,
    ) -> list[ContentVariant]:
        variation_count = count if count is not None else random.randint(10, 20)
        triggers = [
            "curiosity",
            "urgency",
            "fear of missing out",
            "social proof",
            "pain point",
            "aspiration",
            "simplicity",
            "surprise",
            "contrast",
            "before-after",
        ]
        ctas = [
            "Try it while it is trending.",
            "Check it out before the price changes.",
            "See the offer today.",
            "Tap through and compare it yourself.",
            "Grab it before the next wave hits.",
        ]

        variants: list[ContentVariant] = []
        for index in range(variation_count):
            trigger = triggers[index % len(triggers)]
            cta = ctas[index % len(ctas)]
            variants.append(
                ContentVariant(
                    parent_content_id=content.id,
                    hook=f"{content.hook} Here is the {trigger} angle nobody is using yet.",
                    script=(
                        f"{content.script} Variant angle: lead with {trigger}, make the problem "
                        "clear faster, then show the product as the simple next step."
                    ),
                    cta=cta,
                    variation_type=trigger,
                )
            )

        return variants

    @staticmethod
    async def process_scaling(db: AsyncSession) -> dict[str, int]:
        result = await db.execute(
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

        aggressive_scale_count = 0
        variations_generated = 0
        queue_entries: list[ScalingQueue] = []
        variant_rows: list[ContentVariant] = []

        for content, views, likes, clicks, conversions, revenue in result.all():
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
            action = DecisionService.decide_action(content, insights)

            if action == "scale aggressively":
                aggressive_scale_count += 1
                priority = "high"
                variants = await ScalingService.generate_variations(content, random.randint(10, 20))
            elif action == "test variations":
                priority = "medium"
                variants = await ScalingService.generate_variations(content, random.randint(3, 5))
            else:
                continue

            logger.info(
                "action triggered",
                extra={"content_id": content.id, "action": action, "priority": priority},
            )
            variant_rows.extend(variants)
            variations_generated += len(variants)
            queue_entries.append(
                ScalingQueue(
                    content_id=content.id,
                    priority=priority,
                    status="pending",
                )
            )

        db.add_all(variant_rows)
        db.add_all(queue_entries)
        await db.commit()

        queue_size_result = await db.execute(
            select(func.count()).select_from(ScalingQueue).where(ScalingQueue.status == "pending")
        )
        queue_size = int(queue_size_result.scalar_one())

        logger.info("winners detected", extra={"count": aggressive_scale_count})
        logger.info("variations generated", extra={"count": variations_generated})
        logger.info("queue size", extra={"count": queue_size})

        return {
            "winners_detected": aggressive_scale_count,
            "variations_generated": variations_generated,
            "queue_size": queue_size,
        }
