from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    source: str = "manual"
    price: float
    commission: float
    trend_id: int


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    source: str
    price: float
    commission: float
    trend_id: int
    profit_score: float
    created_at: datetime
