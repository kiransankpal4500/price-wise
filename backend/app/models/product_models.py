# Defines Pydantic data schemas for validating request and response payloads
from typing import List, Optional
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
    deliveryEta: Optional[str] = Field(None, description="Estimated delivery time, e.g., 10 mins")
    inStock: bool = Field(True, description="Stock availability status")
    computedScore: Optional[int] = Field(None, description="Calculated 0-100 score from recommendation algorithm")

# Model representing a product across all platform listings
class Product(BaseModel):
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Full title of the product")
    category: str = Field(..., description="Product category name")
    description: Optional[str] = Field(None, description="Detailed product description")
    mainImage: str = Field(..., description="Primary image URL for display")
    platforms: List[Platform] = Field(..., description="Listings of this product across different stores")
    bestPickPlatform: Optional[str] = Field(None, description="Store name identified as the best overall deal")

# Response wrapper model for search endpoint results
class SearchResponse(BaseModel):
    query: Optional[str] = Field(None, description="Search query string executed")
    total: int = Field(..., description="Total count of products matching search")
    results: List[Product] = Field(..., description="List of matched products with computed best picks")
