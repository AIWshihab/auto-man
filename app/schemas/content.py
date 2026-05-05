from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContentCreate(BaseModel):
    product_id: int
    hook: str
    script: str
    cta: str
    status: str = "draft"


class ContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    hook: str
    script: str
    cta: str
    status: str
    created_at: datetime
