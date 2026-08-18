"""
Flipkart India (flipkart.com) scraper adapter using Requests + BeautifulSoup with multi-page pagination.
"""

import logging
import re
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


class FlipkartScraper(BaseScraper):
    """Scraper adapter for Flipkart.com with multi-page pagination."""

    def __init__(self):
        super().__init__("Flipkart")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        headers = {
            "Host": "www.flipkart.com",
            "Referer": "https://www.flipkart.com/",
        }

        all_products: List[ScrapedProduct] = []
        page_metrics: List[Dict[str, Any]] = []
        pages_scraped = 0
        total_elapsed_ms = 0.0
        bot_detected = False
        last_status = 200
        seen_urls = set()

        for page in range(1, MAX_PAGES_PER_SOURCE + 1):
            if len(all_products) >= MAX_PRODUCTS_PER_SOURCE:
                break

            search_url = f"https://www.flipkart.com/search?q={encoded_q}&page={page}"
            html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
                search_url, headers=headers, timeout=12.0
            )

            total_elapsed_ms += elapsed_ms
            last_status = status_code

            if error or not html or bot_blocked:
                if page == 1:
                    logger.warning(
                        f"[FlipkartScraper] Page 1 fetch failed or bot blocked. Status={status_code}, BotBlocked={bot_blocked}, Error={error}"
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
                if sp and sp.price > 0 and sp.product_url not in seen_urls:
                    seen_urls.add(sp.product_url)
                    page_products.append(sp)

            # 2. Parse HTML product containers
            link_elements = soup.select('a[href*="/p/"]')
            for link in link_elements:
                try:
                    href = link.get("href", "")
                    if not href or href in seen_urls:
                        continue

                    full_url = href if href.startswith("http") else f"https://www.flipkart.com{href}"
                    fsn_match = re.search(r"pid=([A-Za-z0-9]+)", href) or re.search(r"/p/itm([A-Za-z0-9]+)", href)
                    fsn = fsn_match.group(1) if fsn_match else ""

                    card = link.find_parent("div", class_=re.compile(r"(_1AtVbE|_2kHMtA|_1xHGKx|_75Wfls|cPHxB3|t-_U2N)"))
                    if not card:
                        card = link

                    title_el = (
                        card.select_one("div._4rR01T")
                        or card.select_one("a.IRyWSu")
                        or card.select_one("a.title")
                        or card.select_one("div.KzB257")
                        or card.select_one("a[title]")
                        or link
                    )
                    title = title_el.get("title") or title_el.get_text(strip=True) if title_el else ""
                    if not title or len(title) < 3:
                        continue

                    price_el = (
                        card.select_one("div._30jeq3")
                        or card.select_one("div.Nx9bqj")
                        or card.select_one("div._1vC4OE")
                    )
                    price = clean_price(price_el.get_text(strip=True) if price_el else None)
                    if not price or price <= 0:
                        continue

                    seen_urls.add(href)
                    seen_urls.add(full_url)

                    orig_el = card.select_one("div._3I9dfO") or card.select_one("div.yRaBrg")
                    orig_price = clean_price(orig_el.get_text(strip=True) if orig_el else None)

                    rating_el = card.select_one("div._3LWZlK") or card.select_one("div.X1b28c")
                    rating = clean_price(rating_el.get_text(strip=True) if rating_el else None)

                    rev_el = card.select_one("span._2_R_ns") or card.select_one("span.WAvF4N")
                    review_count = clean_number(rev_el.get_text(strip=True) if rev_el else None)

                    img_el = card.select_one("img._396cs4") or card.select_one("img._2r_T1I") or card.select_one("img.D9BxA4") or card.select_one("img")
                    img_url = img_el.get("src") if img_el else None

                    page_products.append(
                        ScrapedProduct(
                            source=self.source_name,
                            source_product_id=fsn or str(hash(title) & 0xFFFFFFFF),
                            title=title.strip(),
                            price=price,
                            original_price=orig_price,
                            rating=rating,
                            review_count=review_count,
                            image_url=img_url,
                            product_url=full_url,
                            product_identifiers={"fsn": fsn} if fsn else {},
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
            logger.info(f"[FlipkartScraper] Page {page} -> {len(page_products)} products extracted.")
            all_products.extend(page_products)

            # Check next page
            nav_links = soup.select("a._1LKTO3")
            has_next = any("Next" in a.get_text() for a in nav_links) or len(nav_links) > 0
            if not has_next:
                break

        success = len(all_products) > 0
        logger.info(f"[FlipkartScraper] Total -> {len(all_products)} products across {pages_scraped} page(s).")

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
