"""
Requests / HTTP client scraper module for PriceWise.
Performs HTTP requests with rotateable modern desktop headers, SSL verification options,
and bot challenge / CAPTCHA detection.
"""

import asyncio
import logging
import random
import time
from typing import Dict, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

# Curated browser User-Agent headers
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0",
]

BOT_KEYWORDS = [
    "captcha",
    "robot check",
    "access denied",
    "blocked",
    "security check",
    "please verify you are a human",
    "unusual traffic",
    "perimeterx",
    "cloudflare",
]


def get_default_headers(custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Generates modern browser request headers."""
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }
    if custom_headers:
        headers.update(custom_headers)
    return headers


def is_bot_challenge(html_content: str, status_code: int) -> bool:
    """Detects if response HTML is a CAPTCHA or bot challenge page."""
    if status_code in (403, 429, 503):
        return True
    
    if not html_content or len(html_content) < 500:
        return True

    lower_html = html_content[:4000].lower()
    for kw in BOT_KEYWORDS:
        if kw in lower_html:
            return True
            
    return False


def fetch_url_sync(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    timeout: float = 10.0,
) -> Tuple[Optional[str], int, float, bool, Optional[str]]:
    """
    Synchronous HTTP fetcher using requests.
    Returns (html_content, status_code, response_time_ms, is_bot_blocked, error_message).
    """
    start_time = time.time()
    req_headers = get_default_headers(headers)

    try:
        session = requests.Session()
        resp = session.get(
            url,
            headers=req_headers,
            params=params,
            timeout=timeout,
            allow_redirects=True,
        )
        elapsed_ms = (time.time() - start_time) * 1000.0
        bot_blocked = is_bot_challenge(resp.text, resp.status_code)
        
        return resp.text, resp.status_code, elapsed_ms, bot_blocked, None
    except requests.Timeout:
        elapsed_ms = (time.time() - start_time) * 1000.0
        return None, 408, elapsed_ms, False, "Request timeout"
    except requests.RequestException as e:
        elapsed_ms = (time.time() - start_time) * 1000.0
        return None, 500, elapsed_ms, False, str(e)


async def fetch_url_async(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, str]] = None,
    timeout: float = 10.0,
) -> Tuple[Optional[str], int, float, bool, Optional[str]]:
    """Async wrapper around fetch_url_sync to keep event loop unblocked."""
    return await asyncio.to_thread(fetch_url_sync, url, headers, params, timeout)
