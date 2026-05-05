from __future__ import annotations

import asyncio
import logging
import random

from app.schemas.trend import TrendCreate
from app.core.config import settings

logger = logging.getLogger(__name__)


class TrendService:
    @staticmethod
    async def fetch_trends() -> list[TrendCreate]:
        if settings.google_trends_enabled:
            try:
                trends = await asyncio.wait_for(
                    asyncio.to_thread(TrendService._fetch_google_trends),
                    timeout=20,
                )
                logger.info("trends fetched from google trends", extra={"count": len(trends)})
                return trends
            except Exception as exc:
                logger.warning("google trends fetch failed, using mock fallback: %s", exc)

        trends = TrendService._mock_trends()
        logger.info("trends fetched from fallback", extra={"count": len(trends)})
        return trends

    @staticmethod
    def _fetch_google_trends() -> list[TrendCreate]:
        from pytrends.request import TrendReq

        pytrends = TrendReq(hl="en-GB", tz=0, timeout=(5, 15), retries=1, backoff_factor=0.2)
        searches = pytrends.trending_searches(pn="united_kingdom")
        keywords = [str(keyword) for keyword in searches[0].head(20).tolist()]

        scores_by_keyword: dict[str, float] = {}
        for index in range(0, len(keywords), 5):
            batch = keywords[index : index + 5]
            pytrends.build_payload(batch, geo="GB", timeframe="now 7-d")
            interest = pytrends.interest_over_time()
            for keyword in batch:
                if keyword in interest:
                    scores_by_keyword[keyword] = float(interest[keyword].max())

        trends: list[TrendCreate] = []
        for index, keyword in enumerate(keywords[:20]):
            trend_score = scores_by_keyword.get(keyword)
            if trend_score is None:
                trend_score = max(100 - (index * 4), 50)

            trends.append(
                TrendCreate(
                    keyword=keyword,
                    category="general",
                    trend_score=round(max(0, min(trend_score, 100)), 2),
                    velocity="rising",
                    competition_score=round(random.uniform(40, 80), 2),
                )
            )

        return trends[:20]

    @staticmethod
    def _mock_trends() -> list[TrendCreate]:
        keywords = [
            "portable blender",
            "sleep aid gummies",
            "standing desk converter",
            "home pilates kit",
            "cold plunge tub",
            "smart water bottle",
            "wireless car vacuum",
            "led therapy mask",
            "pet calming bed",
            "travel espresso maker",
        ]
        categories = [
            "Fitness",
            "Health",
            "Productivity",
            "Beauty",
            "Pets",
            "Travel",
            "Home",
            "Tech",
            "Lifestyle",
            "Wellness",
        ]

        trends: list[TrendCreate] = []
        for i in range(10):
            trends.append(
                TrendCreate(
                    keyword=keywords[i],
                    category=categories[i],
                    trend_score=round(random.uniform(60, 100), 2),
                    velocity="rising",
                    competition_score=round(random.uniform(40, 80), 2),
                )
            )
        return trends
