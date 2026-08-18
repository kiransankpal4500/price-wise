# Cache service — reads/writes product data from SQLite and enforces freshness rules
import asyncio
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Tuple

from app.database import get_db
from app.config import FRESH_CACHE_HOURS, STALE_CACHE_HOURS
from app.models.product_models import Product, Platform
from app.services.url_validator import sanitize_product_url

logger = logging.getLogger(__name__)

CACHE_FRESH = "fresh"
CACHE_STALE = "stale"
CACHE_VERY_STALE = "very_stale"
CACHE_EMPTY = "empty"

_REFRESH_LOCKS: Dict[str, asyncio.Lock] = {}
_LOCK_REGISTRY_LOCK = asyncio.Lock()


async def _get_refresh_lock(key: str) -> asyncio.Lock:
    """Returns a per-key async lock — creates one if it does not exist yet."""
    async with _LOCK_REGISTRY_LOCK:
        if key not in _REFRESH_LOCKS:
            _REFRESH_LOCKS[key] = asyncio.Lock()
        return _REFRESH_LOCKS[key]


def normalize_search_key(query: Optional[str]) -> str:
    """Normalises a search query to a consistent cache key."""
    if not query:
        return "__trending__"
    return re.sub(r"\s+", " ", query.strip().lower())


def _parse_utc(ts_str: Optional[str]) -> Optional[datetime]:
    """Parses an ISO timestamp string to a timezone-aware UTC datetime."""
    if not ts_str:
        return None
    try:
        dt = datetime.fromisoformat(ts_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def _get_cache_status(fetched_at_str: Optional[str]) -> str:
    """Determines cache freshness based on when data was last fetched."""
    fetched_at = _parse_utc(fetched_at_str)
    if fetched_at is None:
        return CACHE_EMPTY

    age_hours = (datetime.now(timezone.utc) - fetched_at).total_seconds() / 3600

    if age_hours < FRESH_CACHE_HOURS:
        return CACHE_FRESH
    elif age_hours < STALE_CACHE_HOURS:
        return CACHE_STALE
    else:
        return CACHE_VERY_STALE


async def get_cached_products(search_key: str) -> Tuple[List[Product], str, Optional[str]]:
    """
    Reads products from cache matching search_key, product name, or category.
    Returns (products, cache_status, last_updated_iso_str).
    """
    db = await get_db()
    try:
        pattern = f"%{search_key}%"
        if search_key == "__trending__":
            sql = """
                SELECT DISTINCT product_id, name, category, description, image_url,
                                MAX(fetched_at) as fetched_at
                FROM cached_products
                GROUP BY product_id
                ORDER BY fetched_at DESC
                LIMIT 16
            """
            params = ()
        else:
            sql = """
                SELECT DISTINCT product_id, name, category, description, image_url,
                                MAX(fetched_at) as fetched_at
                FROM cached_products
                WHERE search_key = ? OR search_key LIKE ? OR LOWER(name) LIKE ?
                GROUP BY product_id
                ORDER BY fetched_at DESC
            """
            params = (search_key, pattern, pattern)

        cursor = await db.execute(sql, params)
        product_rows = await cursor.fetchall()


        if not product_rows:
            return [], CACHE_EMPTY, None

        oldest_fetch = min(
            (row["fetched_at"] for row in product_rows if row["fetched_at"]),
            default=None,
        )
        cache_status = _get_cache_status(oldest_fetch)
        last_updated = oldest_fetch

        products: List[Product] = []
        for prod_row in product_rows:
            prod_id = prod_row["product_id"]

            plat_cursor = await db.execute(
                """
                SELECT DISTINCT platform, price, original_price, rating, review_count,
                                image_url, product_url, delivery_info, availability,
                                discount, raw_api_data
                FROM cached_products
                WHERE product_id = ?
                ORDER BY price ASC
                """,
                (prod_id,),
            )
            platform_rows = await plat_cursor.fetchall()

            platforms: List[Platform] = []
            seen_platforms = set()
            for pl in platform_rows:
                p_name = pl["platform"]
                if p_name in seen_platforms:
                    continue
                seen_platforms.add(p_name)
                verified_url = sanitize_product_url(pl["product_url"], p_name)
                platforms.append(
                    Platform(
                        platformName=p_name,
                        price=float(pl["price"] or 0),
                        originalPrice=float(pl["original_price"]) if pl["original_price"] else None,
                        rating=float(pl["rating"] or 0),
                        reviewCount=int(pl["review_count"]) if pl["review_count"] is not None else None,
                        imageUrl=pl["image_url"] or "",
                        deeplink=verified_url or "",
                        product_url=verified_url,
                        deliveryEta=pl["delivery_info"],
                        inStock=bool(pl["availability"]) if pl["availability"] is not None else True,
                    )
                )

            if platforms:
                products.append(
                    Product(
                        id=prod_id,
                        name=prod_row["name"] or "Unknown Product",
                        category=prod_row["category"] or "General",
                        description=prod_row["description"],
                        mainImage=platforms[0].imageUrl,
                        platforms=platforms,
                        bestPickPlatform=None,
                    )
                )

        return products, cache_status, last_updated
    finally:
        await db.close()


async def save_products_to_cache(products: List[Product], search_key: str) -> None:
    """Upserts products and their platform listings into the cache database."""
    now = datetime.now(timezone.utc).isoformat()
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=STALE_CACHE_HOURS)).isoformat()

    db = await get_db()
    try:
        for product in products:
            for platform in product.platforms:
                verified_url = sanitize_product_url(
                    platform.product_url or platform.deeplink,
                    platform.platformName,
                )
                raw_data = {
                    "product_id": product.id,
                    "name": product.name,
                    "category": product.category,
                    "platform": platform.platformName,
                    "price": platform.price,
                    "product_url": verified_url,
                }
                await db.execute(
                    """
                    INSERT INTO cached_products (
                        product_id, platform, name, category, description,
                        image_url, product_url, price, original_price, discount,
                        rating, review_count, availability, delivery_info,
                        raw_api_data, search_key, fetched_at, expires_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(product_id, platform) DO UPDATE SET
                        name = excluded.name,
                        category = excluded.category,
                        description = excluded.description,
                        image_url = excluded.image_url,
                        product_url = excluded.product_url,
                        price = excluded.price,
                        original_price = excluded.original_price,
                        rating = excluded.rating,
                        review_count = excluded.review_count,
                        availability = excluded.availability,
                        delivery_info = excluded.delivery_info,
                        raw_api_data = excluded.raw_api_data,
                        search_key = excluded.search_key,
                        fetched_at = excluded.fetched_at,
                        expires_at = excluded.expires_at,
                        updated_at = excluded.updated_at
                    """,
                    (
                        product.id,
                        platform.platformName,
                        product.name,
                        product.category,
                        product.description,
                        platform.imageUrl,
                        verified_url,
                        platform.price,
                        platform.originalPrice,
                        None,
                        platform.rating,
                        platform.reviewCount,
                        1 if platform.inStock else 0,
                        platform.deliveryEta,
                        json.dumps(raw_data),
                        search_key,
                        now,
                        expires_at,
                        now,
                    ),
                )
        await db.commit()
        logger.info(f"[Cache] Saved {len(products)} product(s) for key='{search_key}'")
    except Exception as e:
        logger.error(f"[Cache] Failed to save products: {e}")
    finally:
        await db.close()


async def get_cache_db_stats() -> dict:
    """Returns cache statistics for admin monitoring."""
    db = await get_db()
    try:
        total_cursor = await db.execute("SELECT COUNT(DISTINCT product_id) as cnt FROM cached_products")
        total_row = await total_cursor.fetchone()

        oldest_cursor = await db.execute("SELECT MIN(fetched_at) as oldest FROM cached_products")
        oldest_row = await oldest_cursor.fetchone()

        newest_cursor = await db.execute("SELECT MAX(fetched_at) as newest FROM cached_products")
        newest_row = await newest_cursor.fetchone()

        return {
            "total_cached_products": total_row["cnt"] if total_row else 0,
            "oldest_cached_data": oldest_row["oldest"] if oldest_row else None,
            "newest_cached_data": newest_row["newest"] if newest_row else None,
        }
    finally:
        await db.close()


async def try_acquire_refresh_lock(search_key: str) -> bool:
    """Attempts to acquire the refresh lock for a search key without blocking."""
    lock = await _get_refresh_lock(search_key)
    return lock.locked() is False and await _try_lock(lock)


async def _try_lock(lock: asyncio.Lock) -> bool:
    """Non-blocking lock acquisition helper."""
    if lock.locked():
        return False
    try:
        await asyncio.wait_for(lock.acquire(), timeout=0.01)
        return True
    except (asyncio.TimeoutError, Exception):
        return False


def release_refresh_lock(search_key: str) -> None:
    """Releases the refresh lock for a search key."""
    if search_key in _REFRESH_LOCKS:
        lock = _REFRESH_LOCKS[search_key]
        if lock.locked():
            try:
                lock.release()
            except RuntimeError:
                pass
