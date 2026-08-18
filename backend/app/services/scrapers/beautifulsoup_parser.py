"""
BeautifulSoup HTML & JSON-LD parser module for PriceWise.
Parses structured JSON-LD (Schema.org Product/Offer/AggregateRating), OpenGraph meta tags,
and CSS selectors into normalized ScrapedProduct instances.
"""

import json
import logging
import re
from typing import Dict, List, Optional, Any, Union
from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import ScrapedProduct

logger = logging.getLogger(__name__)


def clean_price(price_raw: Any) -> Optional[float]:
    """Cleans a raw price string or number into a float value."""
    if price_raw is None:
        return None
    if isinstance(price_raw, (int, float)):
        return float(price_raw)
    
    s_val = str(price_raw).replace(",", "").strip()
    # Find numbers with optional decimals
    match = re.search(r"(\d+(?:\.\d+)?)", s_val)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def clean_number(num_raw: Any) -> Optional[int]:
    """Cleans a raw review count or rating integer/float."""
    if num_raw is None:
        return None
    if isinstance(num_raw, (int, float)):
        return int(num_raw)
    
    s_val = str(num_raw).replace(",", "").strip()
    match = re.search(r"(\d+)", s_val)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None


def parse_json_ld(soup: BeautifulSoup, source_name: str, base_url: str = "") -> List[Dict[str, Any]]:
    """
    Finds and parses all <script type="application/ld+json"> blocks in soup.
    Handles single objects, lists of objects, and @graph arrays.
    Returns list of extracted raw product dictionaries.
    """
    extracted_products: List[Dict[str, Any]] = []
    scripts = soup.find_all("script", type=re.compile(r"application/ld\+json", re.I))

    for script in scripts:
        if not script.string:
            continue
        try:
            data = json.loads(script.string.strip())
        except Exception:
            continue

        items = []
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            if "@graph" in data and isinstance(data["@graph"], list):
                items = data["@graph"]
            else:
                items = [data]

        for item in items:
            if not isinstance(item, dict):
                continue

            item_type = item.get("@type", "")
            if isinstance(item_type, list):
                is_product = any("Product" in str(t) for t in item_type)
            else:
                is_product = "Product" in str(item_type)

            if is_product:
                extracted_products.append(item)

    return extracted_products


def convert_json_ld_to_scraped_product(
    ld_dict: Dict[str, Any],
    source_name: str,
    fallback_url: str = "",
) -> Optional[ScrapedProduct]:
    """Converts a raw Schema.org Product JSON-LD dictionary into a ScrapedProduct."""
    try:
        title = ld_dict.get("name") or ld_dict.get("title")
        if not title or not isinstance(title, str):
            return None

        # Extract Brand
        brand_data = ld_dict.get("brand")
        brand = None
        if isinstance(brand_data, dict):
            brand = brand_data.get("name")
        elif isinstance(brand_data, str):
            brand = brand_data

        # Extract Model & SKU
        model = ld_dict.get("model") if isinstance(ld_dict.get("model"), str) else None
        sku = str(ld_dict.get("sku") or ld_dict.get("productID") or ld_dict.get("gtin13") or ld_dict.get("gtin") or "")

        # Extract Image
        img_data = ld_dict.get("image")
        image_url = None
        if isinstance(img_data, list) and img_data:
            image_url = str(img_data[0]) if isinstance(img_data[0], str) else (img_data[0].get("url") if isinstance(img_data[0], dict) else None)
        elif isinstance(img_data, dict):
            image_url = img_data.get("url")
        elif isinstance(img_data, str):
            image_url = img_data

        # Extract Offers
        offers_data = ld_dict.get("offers")
        offer = {}
        if isinstance(offers_data, list) and offers_data:
            offer = offers_data[0] if isinstance(offers_data[0], dict) else {}
        elif isinstance(offers_data, dict):
            offer = offers_data

        price_raw = offer.get("price") or offer.get("lowPrice") or offer.get("highPrice")
        price = clean_price(price_raw)

        # Availability
        avail_str = str(offer.get("availability") or "")
        availability = "InStock" in avail_str or "http://schema.org/InStock" in avail_str or not avail_str

        # Product URL
        prod_url = offer.get("url") or ld_dict.get("url") or fallback_url
        if not isinstance(prod_url, str) or not prod_url.strip():
            prod_url = fallback_url

        # Rating & Review Count
        rating_data = ld_dict.get("aggregateRating") or {}
        rating = None
        review_count = None
        if isinstance(rating_data, dict):
            rating = clean_price(rating_data.get("ratingValue"))
            review_count = clean_number(rating_data.get("reviewCount") or rating_data.get("ratingCount"))

        if price is None or price <= 0:
            # Missing valid price
            return None

        return ScrapedProduct(
            source=source_name,
            source_product_id=sku or str(hash(title + source_name) & 0xFFFFFFFF),
            title=title.strip(),
            brand=brand.strip() if brand else None,
            model=model.strip() if model else None,
            price=price,
            original_price=clean_price(offer.get("highPrice")),
            currency=str(offer.get("priceCurrency") or "INR"),
            rating=rating,
            review_count=review_count,
            availability=availability,
            seller=offer.get("seller", {}).get("name") if isinstance(offer.get("seller"), dict) else None,
            image_url=image_url,
            product_url=prod_url.strip(),
            product_identifiers={"sku": sku} if sku else {},
            data_source="beautifulsoup",
            confidence=0.95,
        )
    except Exception as e:
        logger.debug(f"[JSON-LD Parser] Exception parsing JSON-LD: {e}")
        return None


def parse_meta_tags(soup: BeautifulSoup, source_name: str, fallback_url: str = "") -> Optional[ScrapedProduct]:
    """Extracts product data from OpenGraph and Schema.org meta tags."""
    try:
        def get_meta(prop_list: List[str]) -> Optional[str]:
            for p in prop_list:
                tag = soup.find("meta", property=p) or soup.find("meta", attrs={"name": p}) or soup.find("meta", attrs={"itemprop": p})
                if tag and tag.get("content"):
                    return tag["content"].strip()
            return None

        title = get_meta(["og:title", "twitter:title", "title"])
        price_raw = get_meta(["og:price:amount", "product:price:amount", "price"])
        image_url = get_meta(["og:image", "twitter:image", "image"])
        prod_url = get_meta(["og:url", "twitter:url"]) or fallback_url
        brand = get_meta(["product:brand", "brand"])

        price = clean_price(price_raw)
        if title and price and price > 0:
            return ScrapedProduct(
                source=source_name,
                source_product_id=str(hash(title + source_name) & 0xFFFFFFFF),
                title=title,
                brand=brand,
                price=price,
                image_url=image_url,
                product_url=prod_url,
                data_source="beautifulsoup",
                confidence=0.85,
            )
    except Exception as e:
        logger.debug(f"[MetaTag Parser] Exception parsing meta tags: {e}")
    return None


def extract_by_selectors(
    soup: BeautifulSoup,
    source_name: str,
    title_selectors: List[str],
    price_selectors: List[str],
    orig_price_selectors: Optional[List[str]] = None,
    image_selectors: Optional[List[str]] = None,
    link_selectors: Optional[List[str]] = None,
    rating_selectors: Optional[List[str]] = None,
    fallback_url: str = "",
) -> List[ScrapedProduct]:
    """
    Extracts products from HTML using lists of CSS selector fallback strategies.
    Supports single product page or product grid pages.
    """
    products: List[ScrapedProduct] = []

    def select_first_text(container: BeautifulSoup | Tag, selectors: List[str]) -> Optional[str]:
        for sel in selectors:
            try:
                el = container.select_one(sel)
                if el:
                    txt = el.get_text(strip=True)
                    if txt:
                        return txt
            except Exception:
                continue
        return None

    def select_first_attr(container: BeautifulSoup | Tag, selectors: List[str], attr: str) -> Optional[str]:
        for sel in selectors:
            try:
                el = container.select_one(sel)
                if el and el.get(attr):
                    return str(el.get(attr)).strip()
            except Exception:
                continue
        return None

    title = select_first_text(soup, title_selectors)
    price_txt = select_first_text(soup, price_selectors)
    price = clean_price(price_txt)

    if title and price and price > 0:
        orig_price = clean_price(select_first_text(soup, orig_price_selectors or []))
        img = select_first_attr(soup, image_selectors or [], "src") or select_first_attr(soup, image_selectors or [], "data-src")
        href = select_first_attr(soup, link_selectors or [], "href") or fallback_url
        rating = clean_price(select_first_text(soup, rating_selectors or []))

        products.append(
            ScrapedProduct(
                source=source_name,
                source_product_id=str(hash(title + source_name) & 0xFFFFFFFF),
                title=title,
                price=price,
                original_price=orig_price,
                rating=rating,
                image_url=img,
                product_url=href,
                data_source="beautifulsoup",
                confidence=0.80,
            )
        )

    return products
