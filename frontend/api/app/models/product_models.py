from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# Model representing an individual e-commerce or quick-commerce platform listing
class Platform(BaseModel):
    platformName: str = Field(..., description="Name of the platform, e.g., Amazon, Blinkit")
    price: float = Field(..., description="Current product selling price")
    originalPrice: Optional[float] = Field(None, description="Original list price before discount")
    rating: float = Field(..., description="User review rating out of 5 stars")
    reviewCount: Optional[int] = Field(None, description="Total review count (optional for quick-commerce)")
    imageUrl: str = Field(..., description="URL of the product image on this store")
    deeplink: str = Field(..., description="Direct link to purchase product on the store")
    product_url: Optional[str] = Field(None, description="Exact product page URL on the store")
    deliveryEta: Optional[str] = Field(None, description="Estimated delivery time, e.g., 10 mins")
    inStock: bool = Field(True, description="Stock availability status")
    computedScore: Optional[int] = Field(None, description="Calculated 0-100 score from recommendation algorithm")
    source_product_id: Optional[str] = Field(None, description="Source platform item ID")
    data_source: Optional[str] = Field(None, description="live / cache / fallback")


# Model representing a product across all platform listings
class Product(BaseModel):
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Full title of the product")
    category: str = Field(..., description="Product category name")
    description: Optional[str] = Field(None, description="Detailed product description")
    mainImage: str = Field(..., description="Primary image URL for display")
    platforms: List[Platform] = Field(..., description="Listings of this product across different stores")
    bestPickPlatform: Optional[str] = Field(None, description="Store name identified as the best overall deal")
    relevanceScore: Optional[float] = Field(None, description="Computed 0.0 - 1.0 relevance score against search query")
    data_source: Optional[str] = Field("cache", description="Data provenance: live / cache / fallback")


# Metadata about where and when product data came from — shown in the frontend
class CacheMetadata(BaseModel):
    last_updated: Optional[str] = Field(None, description="ISO timestamp of when data was last fetched from API")
    cache_status: str = Field("unknown", description="fresh / stale / very_stale / empty / live / fallback")
    data_source: str = Field("cache", description="Source of data: live / cache / fallback")
    message: Optional[str] = Field(None, description="Human-readable status message for the frontend to display")


# Response wrapper model for search endpoint results — includes cache metadata
class SearchResponse(BaseModel):
    query: Optional[str] = Field(None, description="Search query string executed")
    total: int = Field(..., description="Total count of products matching search")
    results: List[Product] = Field(..., description="List of matched products with computed best picks")
    cache_info: Optional[CacheMetadata] = Field(None, description="Cache freshness and data source information")
    query_intent: Optional[Dict[str, Any]] = Field(None, description="Parsed query attributes (brand, model, spec)")


# Response wrapper for trending products endpoint
class TrendingResponse(BaseModel):
    total: int = Field(..., description="Number of trending products returned")
    results: List[Product] = Field(..., description="Trending products with computed scores")
    cache_info: Optional[CacheMetadata] = Field(None, description="Cache freshness and data source information")
