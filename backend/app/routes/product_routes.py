# Defines API endpoints for searching products and viewing platform-by-platform comparisons
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException

from app.models.product_models import Product, SearchResponse
from app.services.quickcommerce_service import fetch_products_from_quickcommerce, fetch_product_by_id
from app.core.ranking import calculate_best_product

router = APIRouter(tags=["Products"])

# Applies sorting to product lists based on user choice (relevance, price_low, price_high, rating)
def apply_product_sorting(products: List[Product], sort_by: str) -> List[Product]:
    if sort_by == 'price_low':
        return sorted(products, key=lambda p: min([pl.price for pl in p.platforms] or [0]))
    elif sort_by == 'price_high':
        return sorted(products, key=lambda p: min([pl.price for pl in p.platforms] or [0]), reverse=True)
    elif sort_by == 'rating':
        return sorted(products, key=lambda p: max([pl.rating for pl in p.platforms] or [0]), reverse=True)
    return products

# Endpoint: GET /search — retrieves products matching search query and calculates Best Pick for each
@router.get("/search", response_model=SearchResponse)
@router.get("/api/search", response_model=SearchResponse)
async def search_products(
    query: Optional[str] = Query(None, description="Search term for product matching"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sortBy: Optional[str] = Query(None, description="Sort order: price_low, price_high, rating"),
    inStockOnly: Optional[bool] = Query(False, description="Filter products to only in-stock platforms")
):
    # Fetch base products from QuickCommerce API service layer
    products = await fetch_products_from_quickcommerce(query=query)

    # Filter products by category if requested
    if category and category.lower() != 'all':
        products = [p for p in products if p.category.lower() == category.lower()]

    # Filter platforms for in-stock items if requested
    if inStockOnly:
        for p in products:
            p.platforms = [pl for pl in p.platforms if pl.inStock]
        products = [p for p in products if len(p.platforms) > 0]

    # Calculate score breakdown and determine Best Pick platform for each product
    processed_products = []
    for prod in products:
        ranking_result = calculate_best_product(prod.platforms)
        prod.platforms = ranking_result["platformsWithScores"]
        prod.bestPickPlatform = ranking_result["bestPickPlatform"]
        processed_products.append(prod)

    # Sort results according to sortBy parameter if provided
    if sortBy:
        processed_products = apply_product_sorting(processed_products, sortBy)

    return SearchResponse(
        query=query,
        total=len(processed_products),
        results=processed_products
    )

# Endpoint: GET /compare/{product_id} — returns detailed platform breakdown and scores for a product
@router.get("/compare/{product_id}", response_model=Product)
@router.get("/api/compare/{product_id}", response_model=Product)
async def compare_product(product_id: str):
    # Fetch target product details by ID
    product = await fetch_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Run recommendation algorithm to compute scores across stores and set Best Pick platform
    ranking_result = calculate_best_product(product.platforms)
    product.platforms = ranking_result["platformsWithScores"]
    product.bestPickPlatform = ranking_result["bestPickPlatform"]

    return product
