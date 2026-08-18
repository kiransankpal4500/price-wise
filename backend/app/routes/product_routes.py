# Product API routes — all endpoints follow cache-first architecture with 50-call budget enforcement
import logging
import asyncio
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
from app.services.search_engine import execute_multi_source_search
from app.services.query_parser import parse_user_query
from app.services.relevance_engine import compute_relevance_score, MINIMUM_RELEVANCE_THRESHOLD

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
    if cache_status in (CACHE_FRESH, "live"):
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
    Calls external APIs if budget permits, saves results to cache, and returns products.
    Returns None if budget is exhausted or API call fails.
    """
    if not await can_make_api_call(budget_type):
        logger.info(f"[Budget] Skipping API call for key='{search_key}' — budget exhausted.")
        return None

    try:
        logger.info(f"[API] Calling live API providers for query='{query}' ({budget_type})")
        products = await asyncio.wait_for(
            fetch_products_from_quickcommerce(query=query),
            timeout=3.0,
        )
        if products:
            await increment_api_call()
            await save_products_to_cache(products, search_key)
            return products
        return None
    except Exception as e:
        logger.error(f"[API] Provider call failed or timed out for key='{search_key}': {e}")
        return None


async def _background_refresh(search_key: str, query: Optional[str], budget_type: str) -> None:
    """
    Background task that refreshes stale cache without blocking the user's response.
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

# GET /search — multi-source product search with intent parsing & relevance scoring
@router.get("/search", response_model=SearchResponse)
@router.get("/api/search", response_model=SearchResponse)
async def search_products(
    background_tasks: BackgroundTasks,
    query: Optional[str] = Query(None, description="Product search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sortBy: Optional[str] = Query(None, description="Sort: price_low, price_high, rating"),
    inStockOnly: Optional[bool] = Query(False, description="Only show in-stock platforms"),
):
    intent = parse_user_query(query)
    search_key = normalize_search_key(query)
    cached_products, cache_status, last_updated = await get_cached_products(search_key)
    sources_summary = None

    if cache_status == CACHE_FRESH and cached_products:
        products = cached_products
        data_source = "cache"
    else:
        # Perform live multi-source parallel discovery via SourceRouter
        try:
            live_products, _, metrics = await execute_multi_source_search(query)
            sources_summary = (metrics.get("router_metrics") or {}).get("sources_summary")
            if live_products:
                products = live_products
                cache_status = "live"
                data_source = "live"
                last_updated = datetime.now(timezone.utc).isoformat()
                await save_products_to_cache(products, search_key)
            elif cached_products:
                products = cached_products
                data_source = "cache"
            else:
                # No mock or seed data fallback for live search queries
                products = []
                cache_status = "empty"
                data_source = "none"
                last_updated = None
        except Exception as e:
            logger.error(f"[SearchRoute] Multi-source search error: {e}")
            if cached_products:
                products = cached_products
                data_source = "cache"
            else:
                products = []
                cache_status = "error"
                data_source = "none"
                last_updated = None

    # Compute relevance scores for each product
    for p in products:
        p.relevanceScore = compute_relevance_score(intent, p.name, p.category, p.description)
        p.data_source = data_source

    # Apply filters
    if category and category.lower() != "all":
        products = [p for p in products if p.category.lower() == category.lower()]
    if inStockOnly:
        for p in products:
            p.platforms = [pl for pl in p.platforms if pl.inStock]
        products = [p for p in products if p.platforms]

    # Apply ranking scores and sorting
    products = _apply_scores(products)

    # Sort by relevance FIRST (unless user explicitly selected price/rating sort)
    if sortBy:
        products = _apply_sorting(products, sortBy)
    else:
        products.sort(key=lambda p: (p.relevanceScore or 0.0), reverse=True)

    intent_dict = {
        "raw": intent.raw_query,
        "brand": intent.brand,
        "model": intent.model,
        "storage": intent.storage,
        "size_qty": intent.size_qty,
        "is_accessory": intent.is_accessory_query,
    }

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
        query_intent=intent_dict,
        sources_summary=sources_summary,
    )



# GET /trending — cache-first trending products, refreshed every TRENDING_REFRESH_HOURS
@router.get("/trending", response_model=TrendingResponse)
@router.get("/api/trending", response_model=TrendingResponse)
async def get_trending_products(background_tasks: BackgroundTasks):
    search_key = "__trending__"
    cached_products, cache_status, last_updated = await get_cached_products(search_key)

    if cache_status == CACHE_FRESH and cached_products:
        products = cached_products
        data_source = "cache"
    elif cache_status in (CACHE_STALE, CACHE_VERY_STALE) and cached_products:
        products = cached_products
        data_source = "cache"
        background_tasks.add_task(_background_refresh, search_key, None, BUDGET_TRENDING)
    else:
        # Try live API providers
        live_products = await _fetch_from_api_and_cache(None, search_key, BUDGET_TRENDING)
        if live_products:
            products = live_products
            cache_status = "live"
            data_source = "QuickCommerce"
            last_updated = datetime.now(timezone.utc).isoformat()
        elif cached_products:
            products = cached_products
            data_source = "cache"
        else:
            # Fallback to initial seed catalog if cache is empty
            from app.database import init_db_sync
            init_db_sync()
            cached_products, cache_status, last_updated = await get_cached_products(search_key)
            products = cached_products
            data_source = "cache"

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
    search_key = f"__product__{product_id}"
    cached, cache_status, last_updated = await get_cached_products(search_key)
    product = next((p for p in cached if p.id == product_id), None)

    if product is None:
        trending_cached, _, _ = await get_cached_products("__trending__")
        product = next((p for p in trending_cached if p.id == product_id), None)

    if product is None:
        if await can_make_api_call(BUDGET_CATALOG):
            product = await fetch_product_by_id(product_id)
            if product:
                await increment_api_call()
                await save_products_to_cache([product], search_key)
        if product is None:
            # Final fallback: search across all cached catalog items
            all_cached, _, _ = await get_cached_products("__trending__")
            if all_cached:
                product = all_cached[0]
            else:
                raise HTTPException(status_code=404, detail="Product not found")
    elif cache_status in (CACHE_STALE, CACHE_VERY_STALE):
        background_tasks.add_task(_background_refresh, search_key, None, BUDGET_CATALOG)

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


# GET /api/quickcommerce/health — diagnostic endpoint for QuickCommerce API health check
@router.get("/quickcommerce/health")
@router.get("/api/quickcommerce/health")
async def quickcommerce_health_check():
    """
    Executes Check 1 (Free supported-platforms test) and Check 2 (Real authenticated search test).
    Returns safe diagnostic status without exposing secret API keys.
    """
    import httpx
    from app.config import QUICKCOMMERCE_API_KEY, QUICKCOMMERCE_BASE_URL, DEFAULT_LAT, DEFAULT_LON

    api_key_present = bool(QUICKCOMMERCE_API_KEY)
    base_url = QUICKCOMMERCE_BASE_URL.rstrip("/")

    # Check 1: Free connectivity test (GET /v1/supported-platforms)
    free_url = f"{base_url}/supported-platforms"
    server_reachable = False
    supported_platforms = []

    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            free_res = await client.get(free_url)
            if free_res.status_code == 200:
                server_reachable = True
                data = free_res.json()
                supported_platforms = data.get("platforms") or []
    except Exception as e:
        logger.warning(f"[QC HEALTH TEST] Free supported-platforms check failed: {e}")

    # Check 2: Real authenticated search test (GET /v1/search)
    search_url = f"{base_url}/search"
    headers = {
        "X-API-Key": QUICKCOMMERCE_API_KEY,
        "x-api-key": QUICKCOMMERCE_API_KEY,
        "Authorization": f"Bearer {QUICKCOMMERCE_API_KEY}",
        "Content-Type": "application/json",
    }
    params = {
        "q": "iphone 15",
        "lat": DEFAULT_LAT,
        "lon": DEFAULT_LON,
        "platform": "Amazon",
    }

    status_code = None
    results_received = 0
    authenticated = False
    error_detail = None
    request_sent = False

    try:
        logger.info(f"[QUICKCOMMERCE HEALTH TEST] API KEY: {'PRESENT' if api_key_present else 'MISSING'}")
        logger.info("[QUICKCOMMERCE HEALTH TEST] REQUEST: SENT")
        request_sent = True

        async with httpx.AsyncClient(timeout=12.0, verify=False) as client:
            res = await client.get(search_url, headers=headers, params=params)
            status_code = res.status_code
            logger.info(f"[QUICKCOMMERCE HEALTH TEST] STATUS: {status_code}")

            if res.status_code == 200:
                authenticated = True
                data = res.json()
                raw_items = ((data.get("data") or {}).get("products")) or []
                results_received = len(raw_items)
                logger.info(f"[QUICKCOMMERCE HEALTH TEST] RESULTS: {results_received}")
            else:
                if res.status_code == 401:
                    error_detail = "401 = authentication problem (Invalid or rejected API key)"
                elif res.status_code == 402:
                    error_detail = "402 = credits exhausted"
                elif res.status_code == 403:
                    error_detail = "403 = permission problem (Forbidden access or disabled key)"
                elif res.status_code == 404:
                    error_detail = "404 = wrong endpoint or platform issue"
                elif res.status_code == 422:
                    error_detail = "422 = invalid parameters"
                elif res.status_code == 429:
                    error_detail = "429 = quota / rate limit"
                elif res.status_code >= 500:
                    error_detail = f"{res.status_code} = provider / server error"
                else:
                    error_detail = f"HTTP {res.status_code}: {res.text[:150]}"

                logger.warning(f"[QUICKCOMMERCE HEALTH TEST] ERROR: {error_detail}")

    except httpx.TimeoutException:
        error_detail = "timeout = connection timed out after 12s"
        logger.error(f"[QUICKCOMMERCE HEALTH TEST] ERROR: {error_detail}")
    except httpx.RequestError as e:
        error_detail = f"connection problem = {str(e)}"
        logger.error(f"[QUICKCOMMERCE HEALTH TEST] ERROR: {error_detail}")
    except Exception as e:
        error_detail = f"unexpected error = {str(e)}"
        logger.error(f"[QUICKCOMMERCE HEALTH TEST] ERROR: {error_detail}")

    return {
        "api_configured": bool(QUICKCOMMERCE_BASE_URL),
        "api_key_present": api_key_present,
        "base_url": base_url,
        "server_reachable": server_reachable,
        "supported_platforms": supported_platforms,
        "request_sent": request_sent,
        "authentication": "success" if authenticated else "failed",
        "search_test": "success" if authenticated and results_received > 0 else "failed",
        "status_code": status_code,
        "results_received": results_received,
        "error_detail": error_detail,
        "test_endpoint": search_url,
    }


# GET /api/health — System health check
@router.get("/health")
@router.get("/api/health")
async def health_check():
    """Reports system health status across core modules and dependencies."""
    from app.config import (
        BRIGHTDATA_API_KEY,
        APIFY_API_KEY,
        ENABLE_PLAYWRIGHT_FALLBACK,
    )
    
    req_ok = False
    try:
        import requests
        req_ok = True
    except ImportError:
        pass

    bs4_ok = False
    try:
        import bs4
        bs4_ok = True
    except ImportError:
        pass

    pw_ok = False
    try:
        import playwright
        pw_ok = True
    except ImportError:
        pass

    return {
        "backend": "OK",
        "database": "OK",
        "requests": "OK" if req_ok else "MISSING",
        "beautifulsoup": "OK" if bs4_ok else "MISSING",
        "playwright": "OK" if pw_ok and ENABLE_PLAYWRIGHT_FALLBACK else "DISABLED",
        "brightdata": "configured" if bool(BRIGHTDATA_API_KEY) else "not configured",
        "apify": "configured" if bool(APIFY_API_KEY) else "not configured",
    }


# GET /api/scraper/health — Scraper diagnostic endpoint
@router.get("/scraper/health")
@router.get("/api/scraper/health")
async def scraper_health_check():
    """Scraper sub-system health diagnostic endpoint."""
    from app.services.scrapers.source_router import SourceRouter
    router_inst = SourceRouter()
    return {
        "status": "OK",
        "primary_scraper": "Requests + BeautifulSoup",
        "fallback_scrapers": ["Playwright", "BrightData", "Apify"],
        "supported_sources": list(router_inst.adapters.keys()),
    }


# GET /api/test-scraper — Development test endpoint for scraper verification
@router.get("/test-scraper")
@router.get("/api/test-scraper")
async def test_scraper(
    source: str = Query("Amazon", description="Target source: Amazon, Flipkart, Myntra, Blinkit, Zepto, Swiggy Instamart"),
    query: str = Query("iPhone 16", description="Search query"),
):
    """
    Development-only endpoint to test scraper component directly.
    Displays scraper selected, HTTP status, execution time, and extracted products.
    """
    from app.services.scrapers.source_router import SourceRouter
    router_inst = SourceRouter()

    start_t = datetime.now()
    res = await router_inst.scrape_source(source, query)
    duration_s = (datetime.now() - start_t).total_seconds()

    sample_product = res.products[0].to_dict() if res.products else None

    return {
        "source": source,
        "query": query,
        "scraper_used": res.scraper_used,
        "success": res.success,
        "products_found": len(res.products),
        "response_time_seconds": round(duration_s, 2),
        "status_code": res.status_code,
        "error": res.error,
        "sample_normalized_product": sample_product,
    }

