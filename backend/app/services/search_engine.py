"""
Multi-Source Parallel Search Engine for PriceWise.
Executes concurrent requests via SourceRouter (Requests + BeautifulSoup primary,
Playwright fallback, BrightData/Apify final fallback).
Aggregates results, computes relevance scores, enforces exact URL integrity,
and removes silent mock product fallbacks.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple

from app.models.product_models import Product, Platform
from app.services.query_parser import parse_user_query, ParsedQuery
from app.services.relevance_engine import compute_relevance_score, MINIMUM_RELEVANCE_THRESHOLD
from app.services.scrapers.source_router import SourceRouter
from app.services.url_validator import sanitize_product_url

logger = logging.getLogger(__name__)


async def execute_multi_source_search(query: Optional[str]) -> Tuple[List[Product], ParsedQuery, Dict[str, Any]]:
    """
    Executes parallel search across all configured data sources using SourceRouter,
    filters by relevance, and preserves exact scraped product URLs.
    """
    intent = parse_user_query(query)
    q_str = query or ""

    logger.info(f"[SearchEngine] Executing live scraper pipeline via SourceRouter for query='{q_str}'...")

    router = SourceRouter()
    live_products, debug_info = await router.execute_search(q_str)

    debug_metrics: Dict[str, Any] = {
        "raw_query": query,
        "normalized_query": intent.normalized_query,
        "brand": intent.brand,
        "model": intent.model,
        "router_metrics": debug_info,
        "total_raw_results": len(live_products),
        "total_relevant_results": 0,
    }

    if not live_products:
        logger.info(f"[SearchEngine] No live products retrieved for query='{q_str}'.")
        return [], intent, debug_metrics

    # Relevance Scoring & URL Validation
    relevant_products: List[Product] = []
    for prod in live_products:
        rel_score = compute_relevance_score(
            intent=intent,
            product_name=prod.name,
            category=prod.category,
            description=prod.description,
        )

        validated_platforms: List[Platform] = []
        for pl in prod.platforms:
            verified_url = sanitize_product_url(pl.product_url or pl.deeplink, pl.platformName)
            pl.product_url = verified_url or pl.product_url
            pl.deeplink = verified_url or pl.deeplink
            validated_platforms.append(pl)

        prod.platforms = validated_platforms

        if rel_score >= MINIMUM_RELEVANCE_THRESHOLD or len(live_products) == 1:
            relevant_products.append(prod)

    debug_metrics["total_relevant_results"] = len(relevant_products)

    # Sort results by Relevance Score DESC
    relevant_products.sort(
        key=lambda p: compute_relevance_score(intent, p.name, p.category, p.description),
        reverse=True,
    )

    return relevant_products, intent, debug_metrics
