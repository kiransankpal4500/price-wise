# Service layer for communicating with the QuickCommerce API and fetching live product data
import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import QUICKCOMMERCE_API_KEY, QUICKCOMMERCE_BASE_URL
from app.models.product_models import Product, Platform

logger = logging.getLogger(__name__)


# ── Field Normalisation ───────────────────────────────────────────────────────

# Normalises raw QuickCommerce platform dict supporting snake_case, camelCase, and alternate field names
def normalize_platform_data(platform_dict: Dict[str, Any]) -> Platform:
    p_name = (
        platform_dict.get("platformName")
        or platform_dict.get("platform_name")
        or platform_dict.get("platform")
        or platform_dict.get("store")
        or "Unknown Store"
    )
    price_val = float(
        platform_dict.get("price") or platform_dict.get("current_price") or 0.0
    )
    orig_price = (
        platform_dict.get("originalPrice")
        or platform_dict.get("original_price")
        or platform_dict.get("mrp")
    )
    rating_val = float(
        platform_dict.get("rating") or platform_dict.get("stars") or 0.0
    )
    rev_cnt = (
        platform_dict.get("reviewCount")
        or platform_dict.get("review_count")
        or platform_dict.get("reviews")
    )
    img_url = (
        platform_dict.get("imageUrl")
        or platform_dict.get("image_url")
        or platform_dict.get("image")
        or ""
    )
    link_url = (
        platform_dict.get("deeplink")
        or platform_dict.get("url")
        or platform_dict.get("link")
        or "#"
    )
    eta_val = (
        platform_dict.get("deliveryEta")
        or platform_dict.get("delivery_eta")
        or platform_dict.get("eta")
    )
    stock_val = (
        platform_dict.get("inStock")
        if platform_dict.get("inStock") is not None
        else platform_dict.get("in_stock", True)
    )

    return Platform(
        platformName=str(p_name),
        price=price_val,
        originalPrice=float(orig_price) if orig_price is not None else None,
        rating=rating_val,
        reviewCount=int(rev_cnt) if rev_cnt is not None else None,
        imageUrl=str(img_url),
        deeplink=str(link_url),
        deliveryEta=str(eta_val) if eta_val is not None else None,
        inStock=bool(stock_val),
        computedScore=platform_dict.get("computedScore"),
    )


# Normalises raw QuickCommerce API product payload supporting multiple key naming conventions
def normalize_product_data(raw_data: Dict[str, Any]) -> Product:
    platforms_raw = raw_data.get("platforms") or raw_data.get("stores") or []
    normalized_platforms = [normalize_platform_data(p) for p in platforms_raw]

    prod_id = (
        raw_data.get("id")
        or raw_data.get("product_id")
        or raw_data.get("_id")
        or ""
    )
    prod_name = (
        raw_data.get("name")
        or raw_data.get("product_name")
        or raw_data.get("title")
        or "Unnamed Product"
    )
    cat_name = raw_data.get("category") or raw_data.get("category_name") or "General"
    desc_val = raw_data.get("description") or raw_data.get("desc")
    main_img = (
        raw_data.get("mainImage")
        or raw_data.get("main_image")
        or raw_data.get("image")
        or (normalized_platforms[0].imageUrl if normalized_platforms else "")
    )
    best_pick = (
        raw_data.get("bestPickPlatform") or raw_data.get("best_pick_platform")
    )

    return Product(
        id=str(prod_id),
        name=str(prod_name),
        category=str(cat_name),
        description=str(desc_val) if desc_val else None,
        mainImage=str(main_img),
        platforms=normalized_platforms,
        bestPickPlatform=str(best_pick) if best_pick else None,
    )


# ── API Call ──────────────────────────────────────────────────────────────────

# Fetches live product listings from QuickCommerce API — NO fallback data here
# Budget checking and caching is the responsibility of the route layer, not this function
async def fetch_products_from_quickcommerce(
    query: Optional[str] = None,
) -> List[Product]:
    headers = {
        "x-api-key": QUICKCOMMERCE_API_KEY,
        "Authorization": f"Bearer {QUICKCOMMERCE_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        url = f"{QUICKCOMMERCE_BASE_URL}/products/search"
        params = {"q": query} if query else {}

        logger.info(f"[QC API] GET {url} | params={params}")
        response = await client.get(url, headers=headers, params=params)

        # Log the raw response structure on first call to help debug field names
        logger.debug(f"[QC API] Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # Log top-level keys so we can verify field mapping is correct
            if isinstance(data, dict):
                logger.info(f"[QC API] Response keys: {list(data.keys())}")
                raw_items = data.get("products") or data.get("results") or data.get("data") or []
            elif isinstance(data, list):
                raw_items = data
            else:
                raw_items = []

            if not raw_items:
                logger.warning("[QC API] Response was 200 but no product items found in payload.")
                return []

            logger.info(f"[QC API] Received {len(raw_items)} product(s) from API.")
            return [normalize_product_data(item) for item in raw_items]

        else:
            # Raise so the route layer knows the call failed and should not increment budget
            logger.error(
                f"[QC API] Request failed: status={response.status_code} body={response.text[:200]}"
            )
            raise RuntimeError(
                f"QuickCommerce API returned status {response.status_code}"
            )


# Fetches a single product by ID — searches all cached keys then falls back to API
async def fetch_product_by_id(product_id: str) -> Optional[Product]:
    """Fetches a single product by doing a search and filtering by ID."""
    all_products = await fetch_products_from_quickcommerce()
    return next((p for p in all_products if p.id == product_id), None)
