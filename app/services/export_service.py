from __future__ import annotations

from app.models.affiliate_link import AffiliateLink
from app.models.content import Content


class ExportService:
    @staticmethod
    def format_for_platform(
        content: Content,
        platform: str,
        affiliate_link: AffiliateLink | None = None,
    ) -> dict[str, str]:
        normalized_platform = platform.lower().strip()
        cta = ExportService._cta_with_link(content, normalized_platform, affiliate_link)

        if normalized_platform == "tiktok":
            return {
                "caption": f"{content.hook} {cta} #TikTokMadeMeBuyIt #Trending #AffiliateFinds",
                "script": content.script,
            }

        if normalized_platform == "instagram":
            return {
                "caption": f"{content.hook}\n\n{cta}",
                "script": content.script,
            }

        if normalized_platform == "youtube":
            return {
                "title": content.hook,
                "description": f"{content.script}\n\n{cta}",
                "script": content.script,
            }

        return {
            "caption": f"{content.hook}\n\n{cta}",
            "script": content.script,
        }

    @staticmethod
    def _cta_with_link(
        content: Content,
        platform: str,
        affiliate_link: AffiliateLink | None,
    ) -> str:
        if affiliate_link is None:
            return content.cta

        tracking_url = (
            f"{affiliate_link.landing_page_url}"
            f"?content_id={content.id}&platform={platform}"
        )
        return f"{content.cta} {tracking_url}"
