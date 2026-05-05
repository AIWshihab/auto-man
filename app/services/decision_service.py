from __future__ import annotations

import logging

from app.models.content import Content
from app.models.content_insights import ContentInsights

logger = logging.getLogger(__name__)


class DecisionService:
    @staticmethod
    def decide_action(content: Content, insights: ContentInsights | None = None) -> str:
        overall_score = insights.overall_score if insights is not None else 0.0

        if overall_score > 0.7:
            action = "scale aggressively"
        elif overall_score > 0.4:
            action = "test variations"
        else:
            action = "drop"

        logger.info(
            "decision made",
            extra={
                "content_id": content.id,
                "overall_score": overall_score,
                "action": action,
            },
        )
        return action
