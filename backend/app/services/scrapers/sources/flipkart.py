"""
Flipkart India (flipkart.com) scraper adapter using Requests + BeautifulSoup.
"""

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


class FlipkartScraper(BaseScraper):
    """Scraper adapter for Flipkart.com."""

    def __init__(self):
        super().__init__("Flipkart")

    async def search(self, query: str) -> ScrapeResult:
        encoded_q = urllib.parse.quote_plus(query)
        search_url = f"https://www.flipkart.com/search?q={encoded_q}"

        headers = {
            "Host": "www.flipkart.com",
            "Referer": "https://www.flipkart.com/",
        }

        html, status_code, elapsed_ms, bot_blocked, error = await fetch_url_async(
            search_url, headers=headers, timeout=12.0
        )

        if error or not html or bot_blocked:
            logger.warning(
                f"[FlipkartScraper] Fetch failed or bot blocked. Status={status_code}, BotBlocked={bot_blocked}, Error={error}"
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

        # 1. Try JSON-LD first
        json_lds = parse_json_ld(soup, self.source_name, search_url)
        for jld in json_lds:
            sp = convert_json_ld_to_scraped_product(jld, self.source_name, search_url)
            if sp and sp.price > 0:
                products.append(sp)

        # 2. Try HTML product link containers `a[href*="/p/"]`
        link_elements = soup.select('a[href*="/p/"]')
        seen_urls = set()

        for link in link_elements:
            try:
                href = link.get("href", "")
                if not href or href in seen_urls:
                    continue

                full_url = href if href.startswith("http") else f"https://www.flipkart.com{href}"
                # Extract FSN / Product ID from Flipkart URL
                fsn_match = re.search(r"pid=([A-Za-z0-9]+)", href) or re.search(r"/p/itm([A-Za-z0-9]+)", href)
                fsn = fsn_match.group(1) if fsn_match else ""

                # Container element (parent grid row or card)
                card = link.find_parent("div", class_=re.compile(r"(_1AtVbE|_2kHMtA|_1xHGKx|_75Wfls|cPHxB3|t-_U2N)"))
                if not card:
                    card = link

                # Title
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

                # Price
                price_el = (
                    card.select_one("div._30jeq3")
                    or card.select_one("div.Nx9bqj")
                    or card.select_one("div._1vC4OE")
                )
                price = clean_price(price_el.get_text(strip=True) if price_el else None)
                if not price or price <= 0:
                    continue

                seen_urls.add(href)

                # Original Price
                orig_el = card.select_one("div._3I9dfO") or card.select_one("div.yRaBrg")
                orig_price = clean_price(orig_el.get_text(strip=True) if orig_el else None)

                # Rating & Review Count
                rating_el = card.select_one("div._3LWZlK") or card.select_one("div.X1b28c")
                rating = clean_price(rating_el.get_text(strip=True) if rating_el else None)

                rev_el = card.select_one("span._2_R_ns") or card.select_one("span.WAvF4N")
                review_count = clean_number(rev_el.get_text(strip=True) if rev_el else None)

                # Image URL
                img_el = card.select_one("img._396cs4") or card.select_one("img._2r_T1I") or card.select_one("img.D9BxA4") or card.select_one("img")
                img_url = img_el.get("src") if img_el else None

                products.append(
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
            except Exception as e:
                logger.debug(f"[FlipkartScraper] Error parsing card: {e}")
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
