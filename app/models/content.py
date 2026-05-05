from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Content(Base):
    __tablename__ = "content"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    product: Mapped["Product"] = relationship(back_populates="content_entries")
    performance_entries: Mapped[list["Performance"]] = relationship(back_populates="content")
    variants: Mapped[list["ContentVariant"]] = relationship(back_populates="parent_content")
    scaling_queue_entries: Mapped[list["ScalingQueue"]] = relationship(back_populates="content")
    click_events: Mapped[list["ClickEvent"]] = relationship(back_populates="content")
    insights: Mapped[list["ContentInsights"]] = relationship(back_populates="content")
