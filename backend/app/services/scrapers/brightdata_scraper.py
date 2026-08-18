"""
BrightData API final fallback scraper module for PriceWise.
Executed only when Requests+BeautifulSoup and Playwright fail to obtain valid product listings.
"""

import logging
import time
from typing import List, Optional
import httpx

from app.config import BRIGHTDATA_API_KEY, BRIGHTDATA_BASE_URL
from app.services.scrapers.base import ScrapedProduct, ScrapeResult
from app.services.scrapers.beautifulsoup_parser import clean_price

logger = logging.getLogger(__name__)


async def scrape_with_brightdata(source_name: str, query: str) -> ScrapeResult:
    """Executes search query via BrightData SERP / E-Commerce collector API."""
    start_time = time.time()
    if not BRIGHTDATA_API_KEY:
        elapsed_ms = (time.time() - start_time) * 1000.0
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="brightdata",
            success=False,
            response_time_ms=elapsed_ms,
            error="BRIGHTDATA_API_KEY not configured",
        )

    headers = {
        "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
        "Content-Type": "application/json",
    }
    url = f"{BRIGHTDATA_BASE_URL.rstrip('/')}/serp/search"
    payload = {
        "query": f"{query} site:{source_name.lower()}.in OR site:{source_name.lower()}.com",
        "country": "in",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.post(url, headers=headers, json=payload)
            elapsed_ms = (time.time() - start_time) * 1000.0

            if res.status_code == 200:
                data = res.json()
                raw_results = data.get("organic") or data.get("results") or []
                products: List[ScrapedProduct] = []

                for item in raw_results:
                    title = item.get("title") or item.get("name")
                    link = item.get("link") or item.get("url")
                    price_val = clean_price(item.get("price"))

                    if title and link:
                        products.append(
                            ScrapedProduct(
                                source=source_name,
                                source_product_id=str(hash(title + link) & 0xFFFFFFFF),
                                title=title,
                                price=price_val or 0.0,
                                product_url=link,
                                data_source="brightdata",
                                confidence=0.75,
                            )
                        )

                success = len(products) > 0
                return ScrapeResult(
                    source=source_name,
                    query=query,
                    scraper_used="brightdata",
                    success=success,
                    products=products,
                    status_code=res.status_code,
                    response_time_ms=elapsed_ms,
                    error=None if success else "No organic results returned from BrightData",
                )
            else:
                return ScrapeResult(
                    source=source_name,
                    query=query,
                    scraper_used="brightdata",
                    success=False,
                    status_code=res.status_code,
                    response_time_ms=elapsed_ms,
                    error=f"BrightData API returned status {res.status_code}",
                )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.warning(f"[BrightDataScraper] API call failed for {source_name}: {e}")
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="brightdata",
            success=False,
            response_time_ms=elapsed_ms,
            error=str(e),
        )
