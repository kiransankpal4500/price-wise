"""
Source Router for PriceWise.
Coordinates multi-source searches using the strict priority execution chain:
1. Requests + BeautifulSoup (PRIMARY)
2. Playwright Headless Browser (JS Fallback)
3. Bright Data / Apify API (Final Fallback)

Normalizes scraped results into PriceWise Product and Platform domain objects.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any

from app.config import (
    ENABLE_PLAYWRIGHT_FALLBACK,
    ENABLE_BRIGHTDATA_FALLBACK,
    ENABLE_APIFY_FALLBACK,
)
from app.models.product_models import Product, Platform
from app.services.scrapers.base import ScrapedProduct, ScrapeResult
from app.services.scrapers.sources.amazon import AmazonScraper
from app.services.scrapers.sources.flipkart import FlipkartScraper
from app.services.scrapers.sources.myntra import MyntraScraper
from app.services.scrapers.sources.blinkit import BlinkitScraper
from app.services.scrapers.sources.zepto import ZeptoScraper
from app.services.scrapers.sources.instamart import InstamartScraper
from app.services.scrapers.playwright_scraper import scrape_with_playwright
from app.services.scrapers.brightdata_scraper import scrape_with_brightdata
from app.services.scrapers.apify_scraper import scrape_with_apify
from app.services.url_validator import sanitize_product_url

logger = logging.getLogger(__name__)


def is_valid_scraped_product(p: ScrapedProduct) -> bool:
    """Validates if a scraped product contains required non-empty fields."""
    if not p.title or len(p.title.strip()) < 2:
        return False
    if not p.product_url or not p.product_url.startswith("http"):
        return False
    if p.price is None or p.price <= 0:
        return False
    return True


class SourceRouter:
    """Master router managing source adapters, scraper priority execution, and result validation."""

    def __init__(self):
        self.adapters = {
            "Amazon": AmazonScraper(),
            "Flipkart": FlipkartScraper(),
            "Myntra": MyntraScraper(),
            "Blinkit": BlinkitScraper(),
            "Zepto": ZeptoScraper(),
            "Swiggy Instamart": InstamartScraper(),
        }

    async def scrape_source(self, source_name: str, query: str) -> ScrapeResult:
        """
        Runs scraper chain for a single source adhering strictly to priority:
        BS4 -> Playwright -> BrightData/Apify.
        """
        adapter = self.adapters.get(source_name)

        # ── Step 1: Requests + BeautifulSoup (PRIMARY) ───────────────────────
        if adapter:
            start_time = time.time()
            bs4_res = await adapter.search(query)
            elapsed_s = time.time() - start_time
            valid_products = [p for p in bs4_res.products if is_valid_scraped_product(p)]

            logger.info(
                f"SEARCH: {query} | SOURCE: {source_name} | SCRAPER: BeautifulSoup | "
                f"STATUS: {bs4_res.status_code or 500} | PRODUCTS: {len(valid_products)} | "
                f"CACHE: MISS | TIME: {elapsed_s:.2f}s"
            )

            if bs4_res.success and valid_products:
                bs4_res.products = valid_products
                return bs4_res

        # ── Step 2: Playwright (JS / DOM Fallback) ───────────────────────────
        if ENABLE_PLAYWRIGHT_FALLBACK:
            start_time = time.time()
            pw_url_map = {
                "Amazon": f"https://www.amazon.in/s?k={query}",
                "Flipkart": f"https://www.flipkart.com/search?q={query}",
                "Myntra": f"https://www.myntra.com/{query}",
                "Blinkit": f"https://blinkit.com/s/?q={query}",
                "Zepto": f"https://www.zeptonow.com/search?query={query}",
                "Swiggy Instamart": f"https://www.swiggy.com/instamart/search?query={query}",
            }
            target_url = pw_url_map.get(source_name, f"https://www.google.com/search?q={query}+{source_name}")
            pw_res = await scrape_with_playwright(source_name, target_url, query)
            elapsed_s = time.time() - start_time
            valid_products = [p for p in pw_res.products if is_valid_scraped_product(p)]

            logger.info(
                f"SEARCH: {query} | SOURCE: {source_name} | SCRAPER: Playwright | "
                f"STATUS: {pw_res.status_code or 500} | PRODUCTS: {len(valid_products)} | "
                f"CACHE: MISS | TIME: {elapsed_s:.2f}s"
            )

            if pw_res.success and valid_products:
                pw_res.products = valid_products
                return pw_res

        # ── Step 3: Bright Data / Apify API (Final Fallback) ──────────────────
        if ENABLE_BRIGHTDATA_FALLBACK:
            start_time = time.time()
            bd_res = await scrape_with_brightdata(source_name, query)
            elapsed_s = time.time() - start_time
            valid_products = [p for p in bd_res.products if is_valid_scraped_product(p)]

            logger.info(
                f"SEARCH: {query} | SOURCE: {source_name} | SCRAPER: BrightData | "
                f"STATUS: {bd_res.status_code or 500} | PRODUCTS: {len(valid_products)} | "
                f"CACHE: MISS | TIME: {elapsed_s:.2f}s"
            )

            if bd_res.success and valid_products:
                bd_res.products = valid_products
                return bd_res

        if ENABLE_APIFY_FALLBACK:
            start_time = time.time()
            apify_res = await scrape_with_apify(source_name, query)
            elapsed_s = time.time() - start_time
            valid_products = [p for p in apify_res.products if is_valid_scraped_product(p)]

            logger.info(
                f"SEARCH: {query} | SOURCE: {source_name} | SCRAPER: Apify | "
                f"STATUS: {apify_res.status_code or 500} | PRODUCTS: {len(valid_products)} | "
                f"CACHE: MISS | TIME: {elapsed_s:.2f}s"
            )

            if apify_res.success and valid_products:
                apify_res.products = valid_products
                return apify_res

        # All scrapers failed for this source
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="none",
            success=False,
            error="All scraper attempts failed or returned 0 valid products",
        )

    async def execute_search(self, query: str) -> Tuple[List[Product], Dict[str, Any]]:
        """
        Executes parallel searches across all configured sources,
        aggregates results, and maps them to PriceWise Product models.
        """
        target_sources = ["Amazon", "Flipkart", "Myntra", "Blinkit", "Zepto", "Swiggy Instamart"]
        tasks = [self.scrape_source(src, query) for src in target_sources]

        start_time = time.time()
        results: List[ScrapeResult] = await asyncio.gather(*tasks, return_exceptions=False)
        total_time_s = time.time() - start_time

        all_scraped_products: List[ScrapedProduct] = []
        source_metrics: List[Dict[str, Any]] = []

        for res in results:
            source_metrics.append({
                "source": res.source,
                "success": res.success,
                "scraper_used": res.scraper_used,
                "products_found": len(res.products),
                "response_time_ms": res.response_time_ms,
                "error": res.error,
            })
            if res.success:
                all_scraped_products.extend(res.products)

        # Map ScrapedProduct instances to PriceWise Product and Platform objects
        domain_products = self._map_to_domain_products(query, all_scraped_products)

        debug_info = {
            "query": query,
            "total_scraped_products": len(all_scraped_products),
            "total_domain_products": len(domain_products),
            "total_time_s": total_time_s,
            "source_metrics": source_metrics,
        }

        return domain_products, debug_info

    def _map_to_domain_products(self, query: str, scraped_items: List[ScrapedProduct]) -> List[Product]:
        """Converts ScrapedProduct records into PriceWise Product domain structures."""
        if not scraped_items:
            return []

        platforms_by_source: List[Platform] = []
        for sp in scraped_items:
            verified_url = sanitize_product_url(sp.product_url, sp.source)
            plat = Platform(
                platformName=sp.source,
                price=sp.price,
                originalPrice=sp.original_price,
                rating=sp.rating or 4.2,
                reviewCount=sp.review_count or 100,
                imageUrl=sp.image_url or "",
                deeplink=verified_url or sp.product_url,
                product_url=verified_url or sp.product_url,
                deliveryEta=sp.delivery_info or "Standard Delivery",
                inStock=sp.availability,
                source_product_id=sp.source_product_id,
                data_source=sp.data_source,
            )
            platforms_by_source.append(plat)

        # Build primary product container
        primary_title = scraped_items[0].title if scraped_items else query.title()
        primary_image = scraped_items[0].image_url or ""
        prod_id = f"pw-{hash(query.strip().lower()) & 0xFFFFFFFF:x}"

        prod = Product(
            id=prod_id,
            name=primary_title,
            category="General",
            description=f"Real-time scraped price comparison for {query}",
            mainImage=primary_image,
            platforms=platforms_by_source,
            bestPickPlatform=platforms_by_source[0].platformName if platforms_by_source else None,
            data_source="live",
        )

        return [prod]
