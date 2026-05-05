from __future__ import annotations

from app.models.content_insights import ContentInsights
from app.models.performance import Performance


class InsightsService:
    @staticmethod
    def analyze_performance(performance: Performance) -> ContentInsights:
        hook_score = min(performance.views / 10_000, 1.0)
        engagement_score = performance.likes / performance.views if performance.views else 0.0
        conversion_score = (
            performance.conversions / performance.clicks if performance.clicks else 0.0
        )
        overall_score = (
            (hook_score * 0.4)
            + (engagement_score * 0.3)
            + (conversion_score * 0.3)
        )

        return ContentInsights(
            content_id=performance.content_id,
            hook_score=round(hook_score, 4),
            engagement_score=round(engagement_score, 4),
            conversion_score=round(conversion_score, 4),
            overall_score=round(overall_score, 4),
        )
