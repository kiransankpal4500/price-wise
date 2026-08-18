"""
Blinkit (blinkit.com) quick-commerce scraper adapter.
"""

import logging
import urllib.parse
from typing import List
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseScraper, ScrapedProduct, ScrapeResult
from app.services.scrapers.requests_scraper import fetch_url_async
from app.services.scrapers.beautifulsoup_parser import (
    parse_json_ld,
    convert_json_ld_to_scraped_product,
    clean_price,
)

logger = logging.getLogger(__name__)


class BlinkitScraper(BaseScraper):
    """Scraper adapter for Blinkit."""

    def __init__(self):
        super().__init__("Blinkit")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        search_url = f"https://blinkit.com/s/?q={encoded_q}"

        headers = {
            "Host": "blinkit.com",
            "Referer": "https://blinkit.com/",
        }

        html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
            search_url, headers=headers, timeout=12.0
        )

        if error or not html or bot_blocked:
            return ScrapeResult(
                source=self.source_name,
                query=query,
                scraper_used="requests_bs4",
                success=False,
                status_code=status_code,
                response_time_ms=elapsed_ms,
                error=error or ("CAPTCHA or Bot Blocked" if bot_blocked else "Empty HTML response"),
                bot_detected=bot_blocked,
            )

        soup = BeautifulSoup(html, "lxml")
        products: List[ScrapedProduct] = []

        # 1. Try JSON-LD
        json_lds = parse_json_ld(soup, self.source_name, search_url)
        for jld in json_lds:
            sp = convert_json_ld_to_scraped_product(jld, self.source_name, search_url)
            if sp and sp.price > 0:
                products.append(sp)

        # 2. Try HTML product card elements
        if not products:
            cards = soup.select("a[href*='/prn/']") or soup.select("div[data-test-id='product-card']")
            seen_urls = set()
            for card in cards:
                try:
                    href = card.get("href", "")
                    if href in seen_urls:
                        continue
                    prod_url = f"https://blinkit.com{href}" if href and not href.startswith("http") else (href or search_url)

                    title_el = card.select_one("div[class*='Product__UpdatedTitle']") or card.select_one("div[class*='title']") or card
                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title or len(title) < 2:
                        continue

                    price_el = card.select_one("div[class*='Product__UpdatedPrice']") or card.select_one("div[class*='price']")
                    price = clean_price(price_el.get_text(strip=True) if price_el else None)

                    if price and price > 0:
                        seen_urls.add(href)
                        products.append(
                            ScrapedProduct(
                                source=self.source_name,
                                source_product_id=str(hash(title) & 0xFFFFFFFF),
                                title=title,
                                price=price,
                                delivery_info="10-15 mins",
                                product_url=prod_url,
                                data_source="beautifulsoup",
                                confidence=0.85,
                            )
                        )
                except Exception:
                    continue

        success = len(products) > 0
        return ScrapeResult(
            source=self.source_name,
            query=query,
            scraper_used="requests_bs4",
            success=success,
            products=products,
            status_code=status_code,
            response_time_ms=elapsed_ms,
            error=None if success else "No products found in HTML content",
            bot_detected=False,
        )
