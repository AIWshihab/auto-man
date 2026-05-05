from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TrendBase(BaseModel):
    keyword: str
    category: str
    trend_score: float
    velocity: str
    competition_score: float


class TrendCreate(TrendBase):
    pass


class TrendResponse(TrendBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
