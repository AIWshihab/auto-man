from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AffiliateLinkCreate(BaseModel):
    product_id: int
    original_url: str


class AffiliateLinkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    original_url: str
    tracking_code: str
    landing_page_url: str
    created_at: datetime
