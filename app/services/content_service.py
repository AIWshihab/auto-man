from __future__ import annotations

import json
import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class ContentService:
    @staticmethod
    async def generate_content(product_name: str) -> dict[str, list[str]]:
        return await ContentService.generate_ai_content(product_name)

    @staticmethod
    async def generate_ai_content(product_name: str) -> dict[str, list[str]]:
        if not settings.openai_api_key:
            logger.warning("openai api key missing, using content fallback")
            return ContentService._fallback_content(product_name)

        prompt = f"""Generate short-form viral marketing content for this product: {product_name}

Return:

* 5 hooks (scroll-stopping, emotional, curiosity-based)
* 3 short scripts (max 30 seconds)
* 3 CTA lines (high conversion)

Style:

* TikTok viral style
* fast-paced
* persuasive
* problem-solution format

Return only valid JSON with this shape:
{{"hooks":["..."],"scripts":["..."],"ctas":["..."]}}"""

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You generate concise affiliate marketing content and return strict JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.8,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                response.raise_for_status()

            data = response.json()
            content = data["choices"][0]["message"]["content"]
            parsed = json.loads(content)
            generated = ContentService._normalize_generated_content(parsed, product_name)
            logger.info("content generated with openai", extra={"product_name": product_name})
            return generated
        except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
            logger.warning("openai content generation failed, using fallback: %s", exc)
            return ContentService._fallback_content(product_name)

    @staticmethod
    def _normalize_generated_content(
        generated: dict[str, object],
        product_name: str,
    ) -> dict[str, list[str]]:
        hooks = ContentService._coerce_string_list(generated.get("hooks"), 5)
        scripts = ContentService._coerce_string_list(generated.get("scripts"), 3)
        ctas = ContentService._coerce_string_list(generated.get("ctas"), 3)

        fallback = ContentService._fallback_content(product_name)
        return {
            "hooks": hooks or fallback["hooks"],
            "scripts": scripts or fallback["scripts"],
            "ctas": ctas or fallback["ctas"],
        }

    @staticmethod
    def _coerce_string_list(value: object, limit: int) -> list[str]:
        if not isinstance(value, list):
            return []

        return [str(item).strip() for item in value if str(item).strip()][:limit]

    @staticmethod
    def _fallback_content(product_name: str) -> dict[str, list[str]]:
        hooks = [
            f"This {product_name} changed my daily routine in 7 days.",
            f"Why everyone is talking about {product_name} right now.",
            f"Stop scrolling if you want better results with {product_name}.",
            f"I wish I found {product_name} before wasting money on alternatives.",
            f"The easiest way to solve this problem might be {product_name}.",
        ]

        scripts = [
            f"I tested {product_name} for a week. Setup was fast, results were noticeable, and it solved a real pain point without extra complexity.",
            f"If you want a smarter way to improve your workflow, {product_name} gives you a practical shortcut with clear value from day one.",
            f"Here is the problem: most people wait too long to fix it. {product_name} gives you a faster path, with less friction and a clear next step.",
        ]

        ctas = [
            f"Tap the link to try {product_name} today.",
            f"Get {product_name} now before this deal ends.",
            f"See why {product_name} is trending today.",
        ]

        return {
            "hooks": hooks,
            "scripts": scripts,
            "ctas": ctas,
        }
