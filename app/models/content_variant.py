from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ContentVariant(Base):
    __tablename__ = "content_variants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    parent_content_id: Mapped[int] = mapped_column(
        ForeignKey("content.id"), nullable=False, index=True
    )
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    script: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str] = mapped_column(Text, nullable=False)
    variation_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    parent_content: Mapped["Content"] = relationship(back_populates="variants")
