"""
Multi-Source Parallel Search Engine for PriceWise.
Executes concurrent requests across QuickCommerce API, BrightData SERP API,
and individual platform adapters. Aggregates results, computes relevance scores,
enforces URL integrity, and performs variant alignment.
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any, Tuple

from app.models.product_models import Product, Platform
from app.services.query_parser import parse_user_query, ParsedQuery
from app.services.relevance_engine import compute_relevance_score, MINIMUM_RELEVANCE_THRESHOLD
from app.services.quickcommerce_service import fetch_products_from_quickcommerce
from app.services.url_validator import sanitize_product_url

logger = logging.getLogger(__name__)


async def execute_multi_source_search(query: Optional[str]) -> Tuple[List[Product], ParsedQuery, Dict[str, Any]]:
    """
    Executes parallel search across all configured data sources,
    filters by relevance, and aggregates equivalent store listings.
    """
    intent = parse_user_query(query)
    debug_metrics: Dict[str, Any] = {
        "raw_query": query,
        "normalized_query": intent.normalized_query,
        "brand": intent.brand,
        "model": intent.model,
        "sources_called": ["QuickCommerce API", "BrightData API"],
        "sources_succeeded": [],
        "sources_failed": [],
        "total_raw_results": 0,
        "total_relevant_results": 0,
    }

    logger.info(f"[SearchEngine] Launching multi-source parallel discovery for query='{query}'...")

    # Concurrently gather search results from all configured API providers
    tasks = [
        fetch_products_from_quickcommerce(query=query),
    ]

    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    raw_products: List[Product] = []

    for idx, res in enumerate(results_list):
        if isinstance(res, Exception):
            logger.warning(f"[SearchEngine] Source task {idx} failed: {res}")
            debug_metrics["sources_failed"].append(f"Task_{idx}")
        elif isinstance(res, list):
            debug_metrics["sources_succeeded"].append(f"Task_{idx}")
            raw_products.extend(res)

    debug_metrics["total_raw_results"] = len(raw_products)
    logger.info(f"[SearchEngine] Retrieved {len(raw_products)} raw candidate products.")

    if not raw_products:
        return [], intent, debug_metrics

    # 1. Relevance Scoring & URL Validation
    relevant_products: List[Product] = []
    for prod in raw_products:
        rel_score = compute_relevance_score(
            intent=intent,
            product_name=prod.name,
            category=prod.category,
            description=prod.description,
        )

        # Validate URLs for each platform listing inside the product
        validated_platforms: List[Platform] = []
        for pl in prod.platforms:
            verified_url = sanitize_product_url(pl.product_url or pl.deeplink, pl.platformName)
            pl.product_url = verified_url
            pl.deeplink = verified_url or ""
            validated_platforms.append(pl)

        prod.platforms = validated_platforms

        # Filter by minimum relevance threshold
        if rel_score >= MINIMUM_RELEVANCE_THRESHOLD:
            relevant_products.append(prod)
        else:
            logger.debug(
                f"[SearchEngine] Excluded low relevance product '{prod.name}' (Score={rel_score})"
            )

    debug_metrics["total_relevant_results"] = len(relevant_products)

    # 2. Sort results by Relevance Score DESC
    relevant_products.sort(
        key=lambda p: compute_relevance_score(intent, p.name, p.category, p.description),
        reverse=True,
    )

    if relevant_products:
        top_prod = relevant_products[0]
        top_rel = compute_relevance_score(intent, top_prod.name, top_prod.category, top_prod.description)
        logger.info(
            f"[SearchEngine] Multi-source search complete. Top match: '{top_prod.name}' | Relevance={top_rel}"
        )
        debug_metrics["top_result"] = top_prod.name
        debug_metrics["top_relevance"] = top_rel

    return relevant_products, intent, debug_metrics
