"""
Base models and abstract interface for all PriceWise scrapers.
Enforces common normalized product schema across all source adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any


@dataclass
class ScrapedProduct:
    """Normalized schema for scraped product results across all platforms."""
    source: str                             # e.g., 'Amazon', 'Flipkart', 'Myntra', 'Blinkit'
    source_product_id: str                  # e.g., ASIN, FSN, or internal store ID
    title: str                              # Product title
    price: float                            # Current offer price
    product_url: str                        # EXACT scraped product URL
    brand: Optional[str] = None             # Brand name
    model: Optional[str] = None             # Model designation
    variant: Optional[str] = None           # Variant description (e.g., '128GB Black')
    original_price: Optional[float] = None  # Original / MRP price
    discount: Optional[float] = None        # Calculated or reported discount %
    currency: str = "INR"                   # Default currency
    rating: Optional[float] = None          # Rating score (0.0 to 5.0)
    review_count: Optional[int] = None      # Total review count
    availability: bool = True               # In-stock status
    seller: Optional[str] = None            # Merchant / Seller name
    delivery_info: Optional[str] = None     # Delivery ETA / shipping info
    image_url: Optional[str] = None         # Primary product image URL
    product_identifiers: Dict[str, Any] = field(default_factory=dict) # SKU, GTIN, ASIN
    scraped_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    data_source: str = "beautifulsoup"      # 'beautifulsoup', 'playwright', 'brightdata', 'apify'
    confidence: float = 1.0                 # Data quality confidence score (0.0 to 1.0)

    def to_dict(self) -> Dict[str, Any]:
        """Converts ScrapedProduct to a dictionary."""
        return {
            "source": self.source,
            "source_product_id": self.source_product_id,
            "title": self.title,
            "brand": self.brand,
            "model": self.model,
            "variant": self.variant,
            "price": self.price,
            "original_price": self.original_price,
            "discount": self.discount,
            "currency": self.currency,
            "rating": self.rating,
            "review_count": self.review_count,
            "availability": self.availability,
            "seller": self.seller,
            "delivery_info": self.delivery_info,
            "image_url": self.image_url,
            "product_url": self.product_url,
            "product_identifiers": self.product_identifiers,
            "scraped_at": self.scraped_at,
            "data_source": self.data_source,
            "confidence": self.confidence,
        }


@dataclass
class ScrapeResult:
    """Result container returned by scraper implementations."""
    source: str
    query: str
    scraper_used: str                       # 'requests_bs4', 'playwright', 'brightdata', 'apify'
    success: bool
    products: List[ScrapedProduct] = field(default_factory=list)
    status_code: Optional[int] = None
    response_time_ms: float = 0.0
    error: Optional[str] = None
    bot_detected: bool = False


class BaseScraper(ABC):
    """Abstract Base Class for all PriceWise source scrapers."""

    def __init__(self, source_name: str):
        self.source_name = source_name

    @abstractmethod
    async def search(self, query: str) -> ScrapeResult:
        """
        Executes search for query on target platform.
        Returns ScrapeResult containing normalized products or failure metadata.
        """
        pass
