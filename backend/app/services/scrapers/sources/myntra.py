"""
Myntra India (myntra.com) scraper adapter using Requests + BeautifulSoup.
"""

import json
import logging
import re
import urllib.parse
from typing import List
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseScraper, ScrapedProduct, ScrapeResult
from app.services.scrapers.requests_scraper import fetch_url_async
from app.services.scrapers.beautifulsoup_parser import (
    parse_json_ld,
    convert_json_ld_to_scraped_product,
    clean_price,
    clean_number,
)

logger = logging.getLogger(__name__)


class MyntraScraper(BaseScraper):
    """Scraper adapter for Myntra.com."""

    def __init__(self):
        super().__init__("Myntra")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        search_url = f"https://www.myntra.com/{encoded_q}"

        headers = {
            "Host": "www.myntra.com",
            "Referer": "https://www.myntra.com/",
        }

        html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
            search_url, headers=headers, timeout=12.0
        )

        if error or not html or bot_blocked:
            logger.warning(
                f"[MyntraScraper] Fetch failed or bot blocked. Status={status_code}, BotBlocked={bot_blocked}, Error={error}"
            )
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

        # 1. Check window.__myx script state object in Myntra HTML
        scripts = soup.find_all("script")
        for s in scripts:
            if s.string and "window.__myx =" in s.string:
                try:
                    js_code = s.string.strip()
                    json_str = js_code.split("window.__myx =", 1)[1].split(";</script>", 1)[0].strip()
                    data = json.loads(json_str)
                    search_data = (data.get("searchData") or {}).get("results") or {}
                    raw_products = search_data.get("products") or []
                    for item in raw_products:
                        p_id = str(item.get("productId") or item.get("landingPageUrl", ""))
                        p_name = str(item.get("productName") or item.get("product", ""))
                        p_brand = str(item.get("brand") or "")
                        title = f"{p_brand} {p_name}".strip() if p_brand else p_name
                        price = clean_price(item.get("price"))
                        mrp = clean_price(item.get("mrp"))
                        rel_url = item.get("landingPageUrl", "")
                        prod_url = f"https://www.myntra.com/{rel_url}" if rel_url and not rel_url.startswith("http") else rel_url

                        rating = clean_price(item.get("rating"))
                        review_count = clean_number(item.get("ratingCount"))
                        img = item.get("images", [{}])[0].get("src") if item.get("images") else item.get("searchImage")

                        if title and price and price > 0:
                            products.append(
                                ScrapedProduct(
                                    source=self.source_name,
                                    source_product_id=p_id,
                                    title=title,
                                    brand=p_brand,
                                    price=price,
                                    original_price=mrp,
                                    rating=rating,
                                    review_count=review_count,
                                    image_url=img,
                                    product_url=prod_url,
                                    data_source="beautifulsoup",
                                    confidence=0.95,
                                )
                            )
                except Exception as e:
                    logger.debug(f"[MyntraScraper] Error parsing window.__myx: {e}")

        # 2. Check JSON-LD fallback
        if not products:
            json_lds = parse_json_ld(soup, self.source_name, search_url)
            for jld in json_lds:
                sp = convert_json_ld_to_scraped_product(jld, self.source_name, search_url)
                if sp and sp.price > 0:
                    products.append(sp)

        # 3. HTML selectors fallback
        if not products:
            cards = soup.select("li.product-base")
            for card in cards:
                try:
                    brand_el = card.select_one("h3.product-brand")
                    name_el = card.select_one("h4.product-product")
                    brand = brand_el.get_text(strip=True) if brand_el else ""
                    name = name_el.get_text(strip=True) if name_el else ""
                    title = f"{brand} {name}".strip() if brand else name

                    price_el = card.select_one("div.product-price span.product-discountedPrice") or card.select_one("div.product-price")
                    price = clean_price(price_el.get_text(strip=True) if price_el else None)

                    link_el = card.select_one("a[target='_blank']") or card.select_one("a[href]")
                    href = link_el.get("href", "") if link_el else ""
                    prod_url = f"https://www.myntra.com/{href}" if href and not href.startswith("http") else href

                    img_el = card.select_one("img.product-thumb") or card.select_one("picture img")
                    img = img_el.get("src") if img_el else None

                    if title and price and price > 0:
                        products.append(
                            ScrapedProduct(
                                source=self.source_name,
                                source_product_id=str(hash(title) & 0xFFFFFFFF),
                                title=title,
                                brand=brand,
                                price=price,
                                image_url=img,
                                product_url=prod_url or search_url,
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
