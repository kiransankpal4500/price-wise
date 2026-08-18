"""
Source Router for PriceWise.
Coordinates multi-source searches using the strict priority execution chain:
1. Requests + BeautifulSoup (PRIMARY)
2. Playwright Headless Browser (JS Fallback)
3. Bright Data / Apify API (Final Fallback)

Normalizes scraped results into PriceWise Product and Platform domain objects,
ensuring multi-page results are collected and distinct product variants remain separate.
"""

import asyncio
import logging
import re
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
                f"STATUS: {bs4_res.status_code or 500} | PAGES: {bs4_res.pages_scraped} | "
                f"PRODUCTS: {len(valid_products)} | TIME: {elapsed_s:.2f}s"
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
                f"TIME: {elapsed_s:.2f}s"
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
                f"TIME: {elapsed_s:.2f}s"
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
                f"TIME: {elapsed_s:.2f}s"
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
        sources_summary: Dict[str, Any] = {}

        for res in results:
            sources_summary[res.source] = {
                "success": res.success,
                "scraper": res.scraper_used,
                "pages_scraped": res.pages_scraped,
                "products_found": len(res.products),
                "response_time_ms": res.response_time_ms,
                "error": res.error,
                "page_metrics": res.page_metrics,
            }
            if res.success:
                all_scraped_products.extend(res.products)

        # Log complete breakdown per source
        logger.info(f"\n==========================================")
        logger.info(f"SEARCH COMPLETE: '{query}' | Total Scraped Raw Items: {len(all_scraped_products)}")
        for src, metrics in sources_summary.items():
            logger.info(
                f"  {src}: Pages Scraped={metrics['pages_scraped']} | Products Found={metrics['products_found']} | Scraper={metrics['scraper']}"
            )
        logger.info(f"==========================================\n")

        # Map ScrapedProduct instances to PriceWise Product and Platform objects
        domain_products = self._map_to_domain_products(query, all_scraped_products)

        debug_info = {
            "query": query,
            "total_scraped_products": len(all_scraped_products),
            "total_domain_products": len(domain_products),
            "total_time_s": total_time_s,
            "sources_summary": sources_summary,
        }

        return domain_products, debug_info

    def _map_to_domain_products(self, query: str, scraped_items: List[ScrapedProduct]) -> List[Product]:
        """
        Converts ScrapedProduct records into PriceWise Product domain structures.
        Groups cross-platform matches for exact same variants while preserving distinct variants as separate products.
        """
        if not scraped_items:
            return []

        # 1. Deduplicate scraped items per source by source + source_product_id or canonical URL
        seen_keys = set()
        deduped_items: List[ScrapedProduct] = []
        for item in scraped_items:
            item_key = f"{item.source}:{item.source_product_id or item.product_url}"
            if item_key not in seen_keys:
                seen_keys.add(item_key)
                deduped_items.append(item)

        # 2. Group items across platforms if they refer to identical titles/variants
        def get_group_key(item: ScrapedProduct) -> str:
            title_clean = re.sub(r"[^\w\s]", "", item.title.lower()).strip()
            title_clean = re.sub(r"\s+", " ", title_clean)
            return title_clean

        grouped_products: Dict[str, List[ScrapedProduct]] = {}
        for item in deduped_items:
            gkey = get_group_key(item)
            if gkey not in grouped_products:
                grouped_products[gkey] = []
            grouped_products[gkey].append(item)

        domain_products: List[Product] = []
        for gkey, items in grouped_products.items():
            primary = items[0]
            platforms: List[Platform] = []
            seen_sources = set()

            for it in items:
                if it.source in seen_sources:
                    continue
                seen_sources.add(it.source)
                verified_url = sanitize_product_url(it.product_url, it.source)
                plat = Platform(
                    platformName=it.source,
                    price=it.price,
                    originalPrice=it.original_price,
                    rating=it.rating or 4.2,
                    reviewCount=it.review_count or 100,
                    imageUrl=it.image_url or "",
                    deeplink=verified_url or it.product_url,
                    product_url=verified_url or it.product_url,
                    deliveryEta=it.delivery_info or "Standard Delivery",
                    inStock=it.availability,
                    source_product_id=it.source_product_id,
                    data_source=it.data_source,
                )
                platforms.append(plat)

            prod_id = f"pw-{hash(primary.title.strip().lower()) & 0xFFFFFFFF:x}"
            prod = Product(
                id=prod_id,
                name=primary.title,
                category="General",
                description=f"Real-time scraped price comparison for {primary.title}",
                mainImage=primary.image_url or "",
                platforms=platforms,
                bestPickPlatform=platforms[0].platformName if platforms else None,
                data_source="live",
            )
            domain_products.append(prod)

        return domain_products
