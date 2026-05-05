from __future__ import annotations

import logging
import random

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.product import Product
from app.models.trend import Trend
from app.schemas.product import ProductCreate, ProductResponse
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/products", tags=["Products"])
logger = logging.getLogger(__name__)


@router.post("/create", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db_session),
) -> Product:
    trend = await db.get(Trend, payload.trend_id)
    if trend is None:
        raise HTTPException(status_code=404, detail="Trend not found")

    virality_score = random.uniform(50, 100)
    profit_score = ScoringService.calculate_profit_score(
        trend_score=trend.trend_score,
        commission=payload.commission,
        virality_score=virality_score,
    )

    product = Product(
        name=payload.name,
        source=payload.source,
        price=payload.price,
        commission=payload.commission,
        trend_id=payload.trend_id,
        profit_score=profit_score,
    )

    db.add(product)
    await db.commit()
    await db.refresh(product)

    logger.info("products created", extra={"count": 1, "product_id": product.id})
    return product


@router.get("", response_model=list[ProductResponse])
async def list_products(db: AsyncSession = Depends(get_db_session)) -> list[Product]:
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    return list(result.scalars().all())
