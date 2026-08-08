# Service layer for communicating with BrightData API for e-commerce search and live price scraping
import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import BRIGHTDATA_API_KEY, BRIGHTDATA_BASE_URL
from app.models.product_models import Product, Platform

logger = logging.getLogger(__name__)


def normalize_brightdata_platform(item: Dict[str, Any], default_platform: str = "Amazon") -> Platform:
    """Normalises raw BrightData result item into a Platform model."""
    platform_name = (
        item.get("source")
        or item.get("platform")
        or item.get("store")
        or item.get("merchant")
        or default_platform
    )
    price_val = float(item.get("price") or item.get("current_price") or item.get("extracted_price") or 0.0)
    orig_price = item.get("original_price") or item.get("mrp") or item.get("initial_price")
    rating_val = float(item.get("rating") or item.get("stars") or 4.5)
    reviews_val = item.get("reviews") or item.get("review_count") or item.get("num_reviews")
    img_url = item.get("image") or item.get("thumbnail") or item.get("image_url") or ""
    link_url = item.get("link") or item.get("url") or item.get("deeplink") or "#"
    eta_val = item.get("delivery") or item.get("eta") or item.get("delivery_time") or "1-2 days"
    stock_val = bool(item.get("in_stock", True))

    return Platform(
        platformName=str(platform_name),
        price=price_val,
        originalPrice=float(orig_price) if orig_price is not None else None,
        rating=rating_val,
        reviewCount=int(reviews_val) if reviews_val is not None else None,
        imageUrl=str(img_url),
        deeplink=str(link_url),
        deliveryEta=str(eta_val) if eta_val is not None else None,
        inStock=stock_val,
    )


async def fetch_products_from_brightdata(query: Optional[str] = None) -> List[Product]:
    """
    Fetches real live product prices from BrightData SERP / E-Commerce Shopping API.
    Uses BRIGHTDATA_API_KEY (c976a32d-f2c0-4e39-97ff-5e7e4761a4d9).
    """
    if not BRIGHTDATA_API_KEY:
        logger.warning("[BrightData] BRIGHTDATA_API_KEY is not configured.")
        return []

    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }

    q = query or "trending electronics"

    async with httpx.AsyncClient(timeout=12.0) as client:
        try:
            # 1. Query BrightData SERP / Shopping API endpoint
            url = f"{BRIGHTDATA_BASE_URL}/serp/req"
            payload = {
                "search_engine": "google_shopping",
                "q": f"{q} site:amazon.in OR site:flipkart.com OR site:blinkit.com",
                "country": "in",
            }
            logger.info(f"[BrightData API] Requesting live e-commerce prices for query='{q}'")
            response = await client.post(url, headers=headers, json=payload)

            if response.status_code == 200:
                data = response.json()
                shopping_results = data.get("shopping_results") or data.get("organic") or []
                logger.info(f"[BrightData API] Received {len(shopping_results)} live shopping items.")

                if not shopping_results:
                    return []

                # Group by product
                platforms = []
                for item in shopping_results[:10]:
                    plat = normalize_brightdata_platform(item)
                    if plat.price > 0:
                        platforms.append(plat)

                if not platforms:
                    return []

                main_prod = Product(
                    id=f"bd-{hash(q) & 0xffffffff:x}",
                    name=q.title(),
                    category="General",
                    description=f"Real-time e-commerce price comparison for {q} powered by BrightData.",
                    mainImage=platforms[0].imageUrl,
                    platforms=platforms,
                    bestPickPlatform=None,
                )
                return [main_prod]

            else:
                logger.warning(f"[BrightData API] Status {response.status_code}: {response.text[:200]}")
                return []

        except Exception as e:
            logger.error(f"[BrightData API] Failed to fetch: {e}")
            return []
