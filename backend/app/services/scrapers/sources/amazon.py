"""
Amazon India (amazon.in) scraper adapter using Requests + BeautifulSoup with multi-page pagination.
"""

import logging
import urllib.parse
from typing import List, Dict, Any
from bs4 import BeautifulSoup

from app.config import MAX_PAGES_PER_SOURCE, MAX_PRODUCTS_PER_SOURCE
from app.services.scrapers.base import BaseScraper, ScrapedProduct, ScrapeResult
from app.services.scrapers.requests_scraper import fetch_url_async
from app.services.scrapers.beautifulsoup_parser import (
    parse_json_ld,
    convert_json_ld_to_scraped_product,
    clean_price,
    clean_number,
)

logger = logging.getLogger(__name__)


class AmazonScraper(BaseScraper):
    """Scraper adapter for Amazon.in with multi-page pagination."""

    def __init__(self):
        super().__init__("Amazon")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        headers = {
            "Host": "www.amazon.in",
            "Referer": "https://www.amazon.in/",
        }

        all_products: List[ScrapedProduct] = []
        page_metrics: List[Dict[str, Any]] = []
        pages_scraped = 0
        total_elapsed_ms = 0.0
        bot_detected = False
        last_status = 200

        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            if len(all_products) >= MAX_PRODUCTS_PER_SOURCE:
                break

            search_url = f"https://www.amazon.in/s?k={encoded_q}&page={page}"
            html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
                search_url, headers=headers, timeout=12.0
            )

            total_elapsed_ms += elapsed_ms
            last_status = status_code

            if error or not html or bot_blocked:
                if page == 1:
                    logger.warning(
                        f"[AmazonScraper] Page 1 fetch failed or bot blocked. Status={status_code}, BotBlocked={bot_blocked}, Error={error}"
                    )
                    return ScrapeResult(
                        source=self.source_name,
                        query=query,
                        scraper_used="requests_bs4",
                        success=False,
                        status_code=status_code,
                        response_time_ms=total_elapsed_ms,
                        error=error or ("CAPTCHA or Bot Blocked" if bot_blocked else "Empty HTML response"),
                        bot_detected=bot_blocked,
                        pages_scraped=pages_scraped,
                        page_metrics=page_metrics,
                    )
                bot_detected = bot_blocked
                break

            pages_scraped += 1
            soup = BeautifulSoup(html, "lxml")
            page_products: List[ScrapedProduct] = []

            # 1. Parse JSON-LD
            json_lds = parse_json_ld(soup, self.source_name, search_url)
            for jld in json_lds:
                sp = convert_json_ld_to_scraped_product(jld, self.source_name, search_url)
                if sp and sp.price > 0:
                    page_products.append(sp)

            # 2. Parse HTML product container cards
            cards = soup.select('div[data-component-type="s-search-result"]')
            for card in cards:
                try:
                    asin = card.get("data-asin", "")
                    if not asin:
                        continue

                    title_el = card.select_one("h2 a span") or card.select_one(".a-text-normal")
                    title = title_el.get_text(strip=True) if title_el else ""
                    if not title:
                        continue

                    link_el = card.select_one("h2 a.a-link-normal") or card.select_one("a.a-link-normal")
                    href = link_el.get("href", "") if link_el else ""
                    if href.startswith("/"):
                        prod_url = f"https://www.amazon.in/dp/{asin}" if asin else f"https://www.amazon.in{href}"
                    elif href.startswith("http"):
                        prod_url = href
                    else:
                        prod_url = f"https://www.amazon.in/dp/{asin}"

                    price_el = card.select_one(".a-price .a-offscreen") or card.select_one(".a-price-whole")
                    price = clean_price(price_el.get_text(strip=True) if price_el else None)
                    if not price or price <= 0:
                        continue

                    orig_el = card.select_one(".a-price.a-text-price .a-offscreen")
                    orig_price = clean_price(orig_el.get_text(strip=True) if orig_el else None)

                    rating_el = card.select_one(".a-icon-alt")
                    rating = None
                    if rating_el:
                        rating_txt = rating_el.get_text(strip=True)
                        rating = clean_price(rating_txt.split("out of")[0] if "out of" in rating_txt else rating_txt)

                    reviews_el = card.select_one('span[aria-label*="ratings"]') or card.select_one("a .a-size-base")
                    review_count = clean_number(reviews_el.get_text(strip=True) if reviews_el else None)

                    img_el = card.select_one("img.s-image")
                    img_url = img_el.get("src") if img_el else None

                    page_products.append(
                        ScrapedProduct(
                            source=self.source_name,
                            source_product_id=asin or str(hash(title) & 0xFFFFFFFF),
                            title=title,
                            price=price,
                            original_price=orig_price,
                            rating=rating,
                            review_count=review_count,
                            image_url=img_url,
                            product_url=prod_url,
                            product_identifiers={"asin": asin} if asin else {},
                            data_source="beautifulsoup",
                            confidence=0.90,
                        )
                    )
                except Exception:
                    continue

            page_metrics.append({
                "page": page,
                "products_found": len(page_products),
                "response_time_ms": elapsed_ms,
            })
            logger.info(f"[AmazonScraper] Page {page} -> {len(page_products)} products extracted.")
            all_products.extend(page_products)

            # Check if next page button exists
            next_btn = soup.select_one("a.s-pagination-next")
            if not next_btn or "a-disabled" in next_btn.get("class", []):
                break

        success = len(all_products) > 0
        logger.info(f"[AmazonScraper] Total -> {len(all_products)} products across {pages_scraped} page(s).")

        return ScrapeResult(
            source=self.source_name,
            query=query,
            scraper_used="requests_bs4",
            success=success,
            products=all_products,
            status_code=last_status,
            response_time_ms=total_elapsed_ms,
            error=None if success else "No products found in HTML pages",
            bot_detected=bot_detected,
            pages_scraped=pages_scraped,
            page_metrics=page_metrics,
        )
