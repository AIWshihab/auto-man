from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content_id: Mapped[int | None] = mapped_column(ForeignKey("content.id"), nullable=True, index=True)
    affiliate_link_id: Mapped[int] = mapped_column(
        ForeignKey("affiliate_links.id"), nullable=False, index=True
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, default="unknown", index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    content: Mapped["Content | None"] = relationship(back_populates="click_events")
    affiliate_link: Mapped["AffiliateLink"] = relationship(back_populates="click_events")
