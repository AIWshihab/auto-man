from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PerformanceCreate(BaseModel):
    content_id: int
    platform: str
    views: int
    likes: int
    clicks: int
    conversions: int
    revenue: float


class PerformanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content_id: int
    platform: str
    views: int
    likes: int
    clicks: int
    conversions: int
    revenue: float
    created_at: datetime


class PerformanceStatusResponse(BaseModel):
    status: str
    views: int
    likes: int
    clicks: int
    conversions: int
    revenue: float
    click_rate: float
    conversion_rate: float
