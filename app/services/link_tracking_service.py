from __future__ import annotations

from uuid import uuid4

from app.core.config import settings


class LinkTrackingService:
    @staticmethod
    def generate_tracking_link(product_id: int, original_url: str) -> dict[str, str]:
        tracking_code = f"p{product_id}-{uuid4().hex[:16]}"
        landing_page_url = f"{settings.app_base_url.rstrip('/')}/track/{tracking_code}"

        return {
            "original_url": original_url,
            "tracking_code": tracking_code,
            "landing_page_url": landing_page_url,
        }
