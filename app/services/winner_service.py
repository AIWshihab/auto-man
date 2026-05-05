from __future__ import annotations

from app.models.performance import Performance


class WinnerService:
    @staticmethod
    def is_winner(performance: Performance) -> str:
        click_rate = performance.clicks / performance.views if performance.views else 0
        conversion_rate = performance.conversions / performance.clicks if performance.clicks else 0

        if performance.views > 10_000 and click_rate > 0.02 and conversion_rate > 0.02:
            return "winner"

        if performance.views < 1_000 or click_rate < 0.01 or conversion_rate < 0.01:
            return "loser"

        return "average"
