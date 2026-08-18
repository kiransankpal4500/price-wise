"""
Playwright headless browser scraper module for PriceWise.
Used as an automatic secondary fallback when Requests + BeautifulSoup encounters
JavaScript-rendering barriers or dynamic page loading requirements.
"""

import asyncio
import logging
import time
from typing import List, Optional
from bs4 import BeautifulSoup

from app.services.scrapers.base import ScrapedProduct, ScrapeResult
from app.services.scrapers.beautifulsoup_parser import (
    parse_json_ld,
    convert_json_ld_to_scraped_product,
    extract_by_selectors,
)

logger = logging.getLogger(__name__)


async def scrape_with_playwright(
    source_name: str,
    search_url: str,
    query: str,
    title_selectors: Optional[List[str]] = None,
    price_selectors: Optional[List[str]] = None,
    wait_selector: Optional[str] = None,
) -> ScrapeResult:
    """
    Launches headless Chromium via Playwright, loads search URL, waits for rendering,
    and extracts product listings.
    """
    start_time = time.time()
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        elapsed_ms = (time.time() - start_time) * 1000.0
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="playwright",
            success=False,
            response_time_ms=elapsed_ms,
            error="Playwright package not installed",
        )

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
            )
            page = await context.new_page()

            # Set route abort for heavy media assets to speed up load time
            await page.route("**/*.{png,jpg,jpeg,gif,svg,mp4,webp}", lambda route: route.abort())

            logger.info(f"[PlaywrightScraper] Navigating to {search_url} for {source_name}...")
            response = await page.goto(search_url, timeout=15000, wait_until="domcontentloaded")
            status_code = response.status if response else 200

            if wait_selector:
                try:
                    await page.wait_for_selector(wait_selector, timeout=5000)
                except Exception:
                    pass

            html_content = await page.content()
            await browser.close()

            elapsed_ms = (time.time() - start_time) * 1000.0
            soup = BeautifulSoup(html_content, "lxml")
            products: List[ScrapedProduct] = []

            # Extract via JSON-LD first
            json_lds = parse_json_ld(soup, source_name, search_url)
            for jld in json_lds:
                sp = convert_json_ld_to_scraped_product(jld, source_name, search_url)
                if sp and sp.price > 0:
                    sp.data_source = "playwright"
                    products.append(sp)

            # Extract via fallback selectors if JSON-LD returns empty
            if not products and title_selectors and price_selectors:
                extracted = extract_by_selectors(
                    soup,
                    source_name,
                    title_selectors=title_selectors,
                    price_selectors=price_selectors,
                    fallback_url=search_url,
                )
                for p_obj in extracted:
                    p_obj.data_source = "playwright"
                    products.append(p_obj)

            success = len(products) > 0
            return ScrapeResult(
                source=source_name,
                query=query,
                scraper_used="playwright",
                success=success,
                products=products,
                status_code=status_code,
                response_time_ms=elapsed_ms,
                error=None if success else "No products found after Playwright rendering",
            )
    except Exception as e:
        elapsed_ms = (time.time() - start_time) * 1000.0
        logger.warning(f"[PlaywrightScraper] Execution failed for {source_name}: {e}")
        return ScrapeResult(
            source=source_name,
            query=query,
            scraper_used="playwright",
            success=False,
            response_time_ms=elapsed_ms,
            error=str(e),
        )
