"""
Apify API fallback scraper module for PriceWise.
Executed only when prior scraper layers fail and APIFY_API_KEY is configured.
"""

import logging
import time
from typing import List
import httpx

from app.config import APIFY_API_KEY
from app.services.scrapers.base import ScrapedProduct, ScrapeResult

logger = logging.getLogger(__name__)


async def scrape_with_apify(source_name: str, query: str) -> ScrapeResult:
    """Executes query via Apify store scraper actor when configured."""
    start_time = time.time()
    if not APIFY_API_KEY:
        elapsed_ms = (time.time() - start_time) * 1000.0
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="apify",
            success=False,
            response_time_ms=elapsed_ms,
            error="APIFY_API_KEY not configured",
        )

    url = f"https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items?token={APIFY_API_KEY}"
    payload = {
        "startUrls": [{"url": f"https://www.google.com/search?q={query}+{source_name}"}],
        "maxItems": 5,
    }

    try:
        async with httpx.AsyncClient(timeout=12.0, verify=False) as client:
            res = await client.post(url, json=payload)
            elapsed_ms = (time.time() - start_time) * 1000.0

            if res.status_code in (200, 201):
                items = res.json()
                products: List[ScrapedProduct] = []
                for it in items:
                    title = it.get("title") or it.get("name")
                    link = it.get("url") or it.get("link")
                    if title and link:
                        products.append(
                            ScrapedProduct(
                                source=source_name,
                                source_product_id=str(hash(title) & 0xFFFFFFFF),
                                title=title,
                                price=float(it.get("price") or 0.0),
                                product_url=link,
                                data_source="apify",
                                confidence=0.70,
                            )
                        )
                success = len(products) > 0
                return ScrapeResult(
                    source=source_name,
                    query=query,
                    scraper_used="apify",
                    success=success,
                    products=products,
                    status_code=res.status_code,
                    response_time_ms=elapsed_ms,
                    error=None if success else "No products returned from Apify dataset",
                )
            else:
                return ScrapeResult(
                    source=source_name,
                    query=query,
                    scraper_used="apify",
                    success=False,
                    status_code=res.status_code,
                    response_time_ms=elapsed_ms,
                    error=f"Apify API returned status {res.status_code}",
                )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.warning(f"[ApifyScraper] Execution failed for {source_name}: {e}")
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="apify",
            success=False,
            response_time_ms=elapsed_ms,
            error=str(e),
        )
