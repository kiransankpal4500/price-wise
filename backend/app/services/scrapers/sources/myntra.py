"""
Myntra India (myntra.com) scraper adapter using Requests + BeautifulSoup with multi-page pagination.
"""

import json
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


class MyntraScraper(BaseScraper):
    """Scraper adapter for Myntra.com with multi-page pagination."""

    def __init__(self):
        super().__init__("Myntra")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        headers = {
            "Host": "www.myntra.com",
            "Referer": "https://www.myntra.com/",
        }

        all_products: List[ScrapedProduct] = []
        page_metrics: List[Dict[str, Any]] = []
        pages_scraped = 0
        total_elapsed_ms = 0.0
        bot_detected = False
        last_status = 200
        seen_ids = set()

        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            if len(all_products) >= MAX_PRODUCTS_PER_SOURCE:
                break

            search_url = f"https://www.myntra.com/{encoded_q}?p={page}"
            html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
                search_url, headers=headers, timeout=12.0
            )

            total_elapsed_ms += elapsed_ms
            last_status = status_code

            if error or not html or bot_blocked:
                if page == 1:
                    logger.warning(
                        f"[MyntraScraper] Page 1 fetch failed or bot blocked. Status={status_code}, BotBlocked={bot_blocked}, Error={error}"
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

            # 1. Parse window.__myx script state
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
                            if p_id in seen_ids:
                                continue

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
                                seen_ids.add(p_id)
                                page_products.append(
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

            # 2. JSON-LD fallback
            if not page_products:
                json_lds = parse_json_ld(soup, self.source_name, search_url)
                for jld in json_lds:
                    sp = convert_json_ld_to_scraped_product(jld, self.source_name, search_url)
                    if sp and sp.price > 0 and sp.source_product_id not in seen_ids:
                        seen_ids.add(sp.source_product_id)
                        page_products.append(sp)

            # 3. HTML selectors fallback
            if not page_products:
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

                        p_id = str(hash(title + (prod_url or "")) & 0xFFFFFFFF)
                        if title and price and price > 0 and p_id not in seen_ids:
                            seen_ids.add(p_id)
                            page_products.append(
                                ScrapedProduct(
                                    source=self.source_name,
                                    source_product_id=p_id,
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

            page_metrics.append({
                "page": page,
                "products_found": len(page_products),
                "response_time_ms": elapsed_ms,
            })
            logger.info(f"[MyntraScraper] Page {page} -> {len(page_products)} products extracted.")
            all_products.extend(page_products)

            if len(page_products) == 0:
                break

        success = len(all_products) > 0
        logger.info(f"[MyntraScraper] Total -> {len(all_products)} products across {pages_scraped} page(s).")

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
