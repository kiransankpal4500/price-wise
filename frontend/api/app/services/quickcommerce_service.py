# Service layer for communicating with QuickCommerce API and BrightData API for real live product data
import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import (
    QUICKCOMMERCE_API_KEY,
    QUICKCOMMERCE_BASE_URL,
    DEFAULT_LAT,
    DEFAULT_LON,
    BRIGHTDATA_API_KEY,
)
from app.models.product_models import Product, Platform
from app.services.brightdata_service import fetch_products_from_brightdata
from app.services.url_validator import sanitize_product_url

logger = logging.getLogger(__name__)


# ── Field Normalisation ───────────────────────────────────────────────────────

# Normalises raw QuickCommerce platform dict supporting snake_case, camelCase, and alternate field names
def normalize_platform_data(platform_dict: Dict[str, Any]) -> Platform:
    p_name = (
        platform_dict.get("platform")
        or platform_dict.get("platformName")
        or platform_dict.get("platform_name")
        or platform_dict.get("store")
        or "Unknown Store"
    )
    price_val = float(
        platform_dict.get("offer_price")
        or platform_dict.get("price")
        or platform_dict.get("current_price")
        or 0.0
    )
    orig_price = (
        platform_dict.get("mrp")
        or platform_dict.get("originalPrice")
        or platform_dict.get("original_price")
    )
    rating_val = float(
        platform_dict.get("rating") or platform_dict.get("stars") or 0.0
    )
    rev_cnt = (
        platform_dict.get("rating_count")
        or platform_dict.get("reviewCount")
        or platform_dict.get("review_count")
        or platform_dict.get("reviews")
    )

    images_list = platform_dict.get("images")
    if isinstance(images_list, list) and images_list:
        img_url = images_list[0]
    else:
        img_url = (
            platform_dict.get("imageUrl")
            or platform_dict.get("image_url")
            or platform_dict.get("image")
            or ""
        )

    # Resolve and strictly validate exact product URL for this store record
    raw_url = (
        platform_dict.get("deeplink")
        or platform_dict.get("product_url")
        or platform_dict.get("productUrl")
        or platform_dict.get("url")
        or platform_dict.get("link")
    )
    verified_url = sanitize_product_url(raw_url, p_name)

    eta_val = (
        platform_dict.get("deliveryEta")
        or platform_dict.get("delivery_eta")
        or platform_dict.get("eta")
        or "10-20 mins"
    )
    stock_val = (
        platform_dict.get("available")
        if platform_dict.get("available") is not None
        else (
            platform_dict.get("inStock")
            if platform_dict.get("inStock") is not None
            else platform_dict.get("in_stock", True)
        )
    )

    source_id = str(platform_dict.get("id") or platform_dict.get("source_product_id") or "")

    return Platform(
        platformName=str(p_name),
        price=price_val,
        originalPrice=float(orig_price) if orig_price is not None else None,
        rating=rating_val,
        reviewCount=int(rev_cnt) if rev_cnt is not None else None,
        imageUrl=str(img_url),
        deeplink=str(verified_url or ""),
        product_url=verified_url,
        deliveryEta=str(eta_val) if eta_val is not None else None,
        inStock=bool(stock_val),
        computedScore=platform_dict.get("computedScore"),
        source_product_id=source_id,
        data_source="live",
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
        data_source="live",
    )


# ── API Calls ──────────────────────────────────────────────────────────────────

# Fetches live product listings from QuickCommerce API and BrightData API
async def fetch_products_from_quickcommerce(
    query: Optional[str] = None,
    lat: Optional[str] = None,
    lon: Optional[str] = None,
) -> List[Product]:
    import asyncio

    headers = {
        "X-API-Key": QUICKCOMMERCE_API_KEY,
        "x-api-key": QUICKCOMMERCE_API_KEY,
        "Authorization": f"Bearer {QUICKCOMMERCE_API_KEY}",
        "Content-Type": "application/json",
    }

    products: List[Product] = []
    q_str = query or "iphone 15"
    latitude = lat or DEFAULT_LAT
    longitude = lon or DEFAULT_LON
    base_url = QUICKCOMMERCE_BASE_URL.rstrip("/")

    target_platforms = ["Amazon", "Flipkart", "BlinkIt", "Zepto", "Swiggy", "Myntra", "Nykaa"]

    async def _fetch_single_platform(client: httpx.AsyncClient, p_name: str):
        url = f"{base_url}/search"
        params = {
            "q": q_str,
            "lat": latitude,
            "lon": longitude,
            "platform": p_name,
        }
        try:
            res = await client.get(url, headers=headers, params=params)
            if res.status_code == 200:
                data = res.json()
                raw_items = (data.get("data") or {}).get("products") or []
                platform_listings = []
                for item in raw_items:
                    if isinstance(item, dict):
                        item["platform"] = p_name
                        plat_obj = normalize_platform_data(item)
                        if plat_obj.price > 0:
                            platform_listings.append(plat_obj)
                return p_name, res.status_code, platform_listings
            return p_name, res.status_code, []
        except Exception as err:
            logger.warning(f"[QC API] Search failed for platform '{p_name}': {err}")
            return p_name, 500, []

    # 1. Primary concurrent call to QuickCommerce API /v1/search across supported stores
    all_platform_listings: List[Platform] = []
    status_codes = []

    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            tasks = [_fetch_single_platform(client, p) for p in target_platforms]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for res in results:
                if isinstance(res, tuple):
                    p_name, status, listings = res
                    status_codes.append(status)
                    if listings:
                        all_platform_listings.extend(listings)

        effective_status = 200 if 200 in status_codes else (status_codes[0] if status_codes else 500)

        if all_platform_listings:
            prod = Product(
                id=f"qc-{hash(q_str) & 0xffffffff:x}",
                name=q_str.title(),
                category="General",
                description=f"Live multi-platform pricing for {q_str}",
                mainImage=all_platform_listings[0].imageUrl,
                platforms=all_platform_listings,
                bestPickPlatform=all_platform_listings[0].platformName,
                data_source="live",
            )
            products.append(prod)

        logger.info(
            f"\n[QuickCommerce]\n"
            f"QUERY: {q_str}\n"
            f"STATUS: {effective_status}\n"
            f"RESULTS: {len(all_platform_listings)}\n"
            f"DATA SOURCE: LIVE\n"
        )
    except Exception as e:
        logger.error(f"[QC API] QuickCommerce call failed: {e}")

    # 2. Call BrightData API using BRIGHTDATA_API_KEY for supplementary or fallback live pricing data
    if BRIGHTDATA_API_KEY and not products:
        try:
            logger.info(f"[BrightData API] Querying live prices for '{q_str}'...")
            bd_products = await fetch_products_from_brightdata(q_str)
            if bd_products:
                logger.info(f"[BrightData API] Retrieved {len(bd_products)} products from BrightData.")
                products.extend(bd_products)
        except Exception as e:
            logger.error(f"[BrightData API] Error querying BrightData: {e}")

    if not products:
        logger.warning("[Data Provider] No products returned from QuickCommerce or BrightData APIs.")
        raise RuntimeError("No live API data returned from QuickCommerce or BrightData providers.")

    return products


# Fetches a single product by ID — searches across all providers then filters by ID
async def fetch_product_by_id(product_id: str) -> Optional[Product]:
    """Fetches a single product by doing a search and filtering by ID."""
    all_products = await fetch_products_from_quickcommerce()
    return next((p for p in all_products if p.id == product_id), None)
