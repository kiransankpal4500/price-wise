"""
URL Validator service for PriceWise.
Verifies that product URLs point to exact product/variant pages,
and flags or rejects generic platform homepages, search result pages,
mismatched store domains, or unverified links.
"""

import logging
from urllib.parse import urlparse
from typing import Optional

logger = logging.getLogger(__name__)

# Known homepage / landing page paths that must be rejected
HOMEPAGE_PATHS = {
    "", "/", "/in", "/in/", "/index.html", "/home", "/store", "/grocery",
    "/minutes", "/instamart", "/fresh", "/electronics", "/fashion"
}

# Domain mapping per platform
PLATFORM_DOMAINS = {
    "amazon": ["amazon.in", "amazon.com", "amzn.to", "amzn.in"],
    "amazon fresh": ["amazon.in", "amazon.com", "amzn.to", "amzn.in"],
    "flipkart": ["flipkart.com", "fkrt.it"],
    "flipkart minutes": ["flipkart.com", "fkrt.it"],
    "blinkit": ["blinkit.com"],
    "zepto": ["zeptonow.com", "zepto.com"],
    "swiggy": ["swiggy.com"],
    "swiggy instamart": ["swiggy.com"],
    "myntra": ["myntra.com"],
    "nykaa": ["nykaa.com"],
    "tata cliq": ["tatacliq.com"],
    "croma": ["croma.com"],
    "reliance digital": ["reliancedigital.in"],
    "decathlon": ["decathlon.in", "decathlon.com"],
    "nike": ["nike.com", "nike.store"],
    "nike store": ["nike.com", "nike.store"],
    "jiomart": ["jiomart.com"],
    "bigbasket": ["bigbasket.com"],
    "dmart": ["dmart.in"],
}


def is_valid_product_url(url: Optional[str], platform_name: Optional[str] = None) -> bool:
    """
    Validates if a URL points to an exact product page on an e-commerce platform.
    Returns False if the URL is missing, invalid, a homepage, a search page, or a domain mismatch.
    """
    if not url or not isinstance(url, str):
        return False

    url_str = url.strip()
    if not url_str or url_str in ("#", "javascript:void(0)", "null", "undefined"):
        return False

    try:
        parsed = urlparse(url_str)
    except Exception as e:
        logger.debug(f"[URLValidator] Failed to parse URL '{url_str}': {e}")
        return False

    if parsed.scheme not in ("http", "https"):
        return False

    netloc = parsed.netloc.lower()
    if not netloc:
        return False

    # 1. Platform domain verification (if platform_name provided)
    if platform_name:
        p_key = platform_name.strip().lower()
        allowed_domains = PLATFORM_DOMAINS.get(p_key)
        if allowed_domains:
            if not any(domain in netloc for domain in allowed_domains):
                logger.warning(
                    f"[URLValidator] Domain mismatch: platform='{platform_name}' "
                    f"does not match URL domain='{netloc}' in '{url_str}'"
                )
                return False

    # 2. Homepage / Root Landing page check
    path = parsed.path.rstrip("/").lower()
    if path in HOMEPAGE_PATHS:
        logger.warning(f"[URLValidator] Rejected homepage URL: '{url_str}' for platform='{platform_name}'")
        return False

    # 3. Search query page check
    if any(sp in path for sp in ["/search", "/s/", "/browse"]) or "s?k=" in url_str or "search_query" in url_str:
        logger.warning(f"[URLValidator] Rejected search result URL: '{url_str}' for platform='{platform_name}'")
        return False

    # 4. Check for product indicator in path (or minimum path depth)
    has_product_pattern = any(
        pat in url_str.lower()
        for pat in [
            "/dp/", "/gp/product/", "/p/", "/prn/", "/product/",
            "/prid/", "/pvid/", "/item/", "/buy", "/pd/", "/p-", "/t/"
        ]
    )

    path_segments = [seg for seg in path.split("/") if seg]
    if len(path_segments) < 1:
        return False

    if not has_product_pattern and len(path_segments) == 1 and len(path_segments[0]) < 10:
        logger.warning(f"[URLValidator] Rejected shallow non-product URL: '{url_str}' for platform='{platform_name}'")
        return False

    return True


def sanitize_product_url(url: Optional[str], platform_name: Optional[str] = None) -> Optional[str]:
    """
    Returns the validated product URL string if valid, or None if invalid.
    Logs diagnostic info when an invalid URL is rejected.
    """
    if is_valid_product_url(url, platform_name):
        return url.strip()

    if url and url not in ("#", "javascript:void(0)"):
        logger.info(
            f"[URLValidator] Sanitized invalid product URL '{url}' for platform='{platform_name}' -> set to None"
        )
    return None
