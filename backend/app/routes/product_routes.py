# Product API routes — all endpoints follow cache-first architecture with 50-call budget enforcement
import logging
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Query, HTTPException, BackgroundTasks

from app.models.product_models import Product, SearchResponse, TrendingResponse, CacheMetadata
from app.services.quickcommerce_service import fetch_products_from_quickcommerce, fetch_product_by_id
from app.services.cache_service import (
    get_cached_products,
    save_products_to_cache,
    normalize_search_key,
    get_cache_db_stats,
    try_acquire_refresh_lock,
    release_refresh_lock,
    CACHE_FRESH,
    CACHE_STALE,
    CACHE_VERY_STALE,
    CACHE_EMPTY,
)
from app.services.api_budget import (
    can_make_api_call,
    increment_api_call,
    get_usage_stats,
    BUDGET_CATALOG,
    BUDGET_SEARCH,
    BUDGET_TRENDING,
)
from app.core.ranking import calculate_best_product
from app.config import TRENDING_REFRESH_HOURS

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Products"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _apply_sorting(products: List[Product], sort_by: Optional[str]) -> List[Product]:
    """Sorts product list by price or rating based on the sortBy parameter."""
    if sort_by == "price_low":
        return sorted(products, key=lambda p: min((pl.price for pl in p.platforms), default=0))
    elif sort_by == "price_high":
        return sorted(products, key=lambda p: min((pl.price for pl in p.platforms), default=0), reverse=True)
    elif sort_by == "rating":
        return sorted(products, key=lambda p: max((pl.rating for pl in p.platforms), default=0), reverse=True)
    return products


def _apply_scores(products: List[Product]) -> List[Product]:
    """Runs the recommendation ranking algorithm on each product's platform list."""
    result = []
    for prod in products:
        ranking = calculate_best_product(prod.platforms)
        prod.platforms = ranking["platformsWithScores"]
        prod.bestPickPlatform = ranking["bestPickPlatform"]
        result.append(prod)
    return result


def _cache_message(cache_status: str, last_updated: Optional[str]) -> str:
    """Returns a human-readable message describing the freshness of the data being returned."""
    if cache_status == CACHE_FRESH:
        return "Data is up to date."
    if last_updated:
        try:
            dt = datetime.fromisoformat(last_updated)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
            if age_hours < 1:
                time_str = "less than an hour ago"
            elif age_hours < 24:
                time_str = f"{int(age_hours)} hour(s) ago"
            else:
                time_str = f"{int(age_hours / 24)} day(s) ago"
            return f"Showing cached data — last updated {time_str}."
        except Exception:
            pass
    return "Showing cached data."


async def _fetch_from_api_and_cache(
    query: Optional[str],
    search_key: str,
    budget_type: str,
) -> Optional[List[Product]]:
    """
    Calls QuickCommerce API if budget permits, saves results to cache, and returns products.
    Returns None if budget is exhausted or the API call fails.
    """
    if not await can_make_api_call(budget_type):
        logger.info(f"[Budget] Skipping API call for key='{search_key}' — budget exhausted.")
        return None

    try:
        logger.info(f"[API] Calling QuickCommerce API for query='{query}' ({budget_type})")
        products = await fetch_products_from_quickcommerce(query=query)
        if products:
            # Increment usage ONLY after a successful API response
            await increment_api_call()
            await save_products_to_cache(products, search_key)
            return products
        return None
    except Exception as e:
        logger.error(f"[API] QuickCommerce API call failed for key='{search_key}': {e}")
        return None


async def _background_refresh(search_key: str, query: Optional[str], budget_type: str) -> None:
    """
    Background task that refreshes stale cache without blocking the user's response.
    Uses a per-key lock so only one refresh runs at a time across concurrent users.
    """
    acquired = await try_acquire_refresh_lock(search_key)
    if not acquired:
        logger.debug(f"[Cache] Refresh already in progress for key='{search_key}' — skipping.")
        return
    try:
        await _fetch_from_api_and_cache(query, search_key, budget_type)
    finally:
        release_refresh_lock(search_key)


# ── Endpoints ─────────────────────────────────────────────────────────────────

# GET /search — cache-first product search with background refresh for stale data
@router.get("/search", response_model=SearchResponse)
@router.get("/api/search", response_model=SearchResponse)
async def search_products(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Query(None, description="Product search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sortBy: Optional[str] = Query(None, description="Sort: price_low, price_high, rating"),
    inStockOnly: Optional[bool] = Query(False, description="Only show in-stock platforms"),
):
    search_key = normalize_search_key(query)
    cached_products, cache_status, last_updated = await get_cached_products(search_key)

    if cache_status == CACHE_FRESH:
        # Return fresh cache immediately — no API call
        products = cached_products
        data_source = "cache"
    elif cache_status in (CACHE_STALE, CACHE_VERY_STALE) and cached_products:
        # Return stale cache immediately, trigger background refresh
        products = cached_products
        data_source = "cache"
        background_tasks.add_task(_background_refresh, search_key, query, BUDGET_SEARCH)
    else:
        # Cache is empty — try the API now, wait for response
        live_products = await _fetch_from_api_and_cache(query, search_key, BUDGET_SEARCH)
        if live_products:
            products = live_products
            cache_status = "live"
            data_source = "QuickCommerce"
            last_updated = datetime.now(timezone.utc).isoformat()
        else:
            return SearchResponse(
                query=query,
                total=0,
                results=[],
                cache_info=CacheMetadata(
                    cache_status="unavailable",
                    data_source="none",
                    message="No fresh results available. Monthly API budget may be exhausted.",
                ),
            )

    # Apply filters
    if category and category.lower() != "all":
        products = [p for p in products if p.category.lower() == category.lower()]
    if inStockOnly:
        for p in products:
            p.platforms = [pl for pl in p.platforms if pl.inStock]
        products = [p for p in products if p.platforms]

    # Apply ranking scores and sorting
    products = _apply_scores(products)
    if sortBy:
        products = _apply_sorting(products, sortBy)

    return SearchResponse(
        query=query,
        total=len(products),
        results=products,
        cache_info=CacheMetadata(
            last_updated=last_updated,
            cache_status=cache_status,
            data_source=data_source,
            message=_cache_message(cache_status, last_updated),
        ),
    )


# GET /trending — cache-first trending products, refreshed every TRENDING_REFRESH_HOURS
@router.get("/trending", response_model=TrendingResponse)
@router.get("/api/trending", response_model=TrendingResponse)
async def get_trending_products(background_tasks: BackgroundTasks):
    search_key = "__trending__"
    cached_products, cache_status, last_updated = await get_cached_products(search_key)

    if cache_status == CACHE_FRESH:
        products = cached_products
        data_source = "cache"
    elif cache_status in (CACHE_STALE, CACHE_VERY_STALE) and cached_products:
        # Return existing cache immediately, refresh in background
        products = cached_products
        data_source = "cache"
        background_tasks.add_task(_background_refresh, search_key, None, BUDGET_TRENDING)
    else:
        # No cache yet — call API synchronously so first user gets real data
        live_products = await _fetch_from_api_and_cache(None, search_key, BUDGET_TRENDING)
        if live_products:
            products = live_products
            cache_status = "live"
            data_source = "QuickCommerce"
            last_updated = datetime.now(timezone.utc).isoformat()
        else:
            return TrendingResponse(
                total=0,
                results=[],
                cache_info=CacheMetadata(
                    cache_status="unavailable",
                    data_source="none",
                    message="Trending data unavailable. API budget may be exhausted.",
                ),
            )

    products = _apply_scores(products)

    return TrendingResponse(
        total=len(products),
        results=products,
        cache_info=CacheMetadata(
            last_updated=last_updated,
            cache_status=cache_status,
            data_source=data_source,
            message=_cache_message(cache_status, last_updated),
        ),
    )


# GET /compare/{product_id} — returns scored platform comparison for a single product
@router.get("/compare/{product_id}", response_model=Product)
@router.get("/api/compare/{product_id}", response_model=Product)
async def compare_product(product_id: str, background_tasks: BackgroundTasks):
    # First try to find this product in the cache
    search_key = f"__product__{product_id}"
    cached, cache_status, last_updated = await get_cached_products(search_key)
    product = next((p for p in cached if p.id == product_id), None)

    if product is None:
        # Try searching by product_id in the general trending/catalog cache
        trending_cached, _, _ = await get_cached_products("__trending__")
        product = next((p for p in trending_cached if p.id == product_id), None)

    if product is None:
        # Fall back to QuickCommerce API if budget allows
        if await can_make_api_call(BUDGET_CATALOG):
            product = await fetch_product_by_id(product_id)
            if product:
                await increment_api_call()
                await save_products_to_cache([product], search_key)
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
    elif cache_status in (CACHE_STALE, CACHE_VERY_STALE):
        # Return stale data, trigger background refresh
        background_tasks.add_task(_background_refresh, search_key, None, BUDGET_CATALOG)

    # Apply ranking scores
    ranking = calculate_best_product(product.platforms)
    product.platforms = ranking["platformsWithScores"]
    product.bestPickPlatform = ranking["bestPickPlatform"]

    return product


# GET /api/system/api-usage — admin monitoring endpoint for API quota and cache health
@router.get("/api/system/api-usage")
async def get_api_usage():
    """Returns monthly API call usage, remaining budget, and cache statistics."""
    usage = await get_usage_stats()
    cache_stats = await get_cache_db_stats()

    return {
        **usage,
        "cache": cache_stats,
    }
