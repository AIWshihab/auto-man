from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="manual")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    commission: Mapped[float] = mapped_column(Float, nullable=False)
    trend_id: Mapped[int] = mapped_column(ForeignKey("trends.id"), nullable=False, index=True)
    profit_score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    trend: Mapped["Trend"] = relationship(back_populates="products")
    content_entries: Mapped[list["Content"]] = relationship(back_populates="product")
    affiliate_links: Mapped[list["AffiliateLink"]] = relationship(back_populates="product")
