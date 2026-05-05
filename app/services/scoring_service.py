from __future__ import annotations


class ScoringService:
    @staticmethod
    def calculate_profit_score(
        trend_score: float,
        commission: float,
        virality_score: float,
    ) -> float:
        profit_score = (
            (trend_score * 0.4)
            + (commission * 0.2)
            + (virality_score * 0.4)
        )
        return round(profit_score, 2)
