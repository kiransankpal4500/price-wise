# Service layer for communicating with external QuickCommerce API and fetching live product data
import httpx
import logging
from typing import List, Optional, Dict, Any
from app.config import QUICKCOMMERCE_API_KEY, QUICKCOMMERCE_BASE_URL
from app.models.product_models import Product, Platform

logger = logging.getLogger(__name__)

# Fallback dataset mirroring the exact QuickCommerce API schema for resilience
FALLBACK_PRODUCTS: List[Dict[str, Any]] = [
    {
        "id": "apple-iphone-15-128gb",
        "name": "Apple iPhone 15 (128 GB) - Black",
        "category": "Electronics",
        "description": "Dynamic Island, 48MP Main Camera with 2x Telephoto, Super Retina XDR Display, and A16 Bionic chip.",
        "mainImage": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80",
        "platforms": [
            {
                "platformName": "Amazon",
                "price": 71290,
                "originalPrice": 79900,
                "rating": 4.6,
                "reviewCount": 4520,
                "imageUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.amazon.in/dp/B0CHX1W1XY",
                "deliveryEta": "Tomorrow, by 10 PM",
                "inStock": True
            },
            {
                "platformName": "Flipkart",
                "price": 69999,
                "originalPrice": 79900,
                "rating": 4.7,
                "reviewCount": 8930,
                "imageUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4",
                "deliveryEta": "2 Days",
                "inStock": True
            },
            {
                "platformName": "JioMart",
                "price": 72490,
                "originalPrice": 79900,
                "rating": 4.3,
                "reviewCount": 410,
                "imageUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.jiomart.com/p/electronics/apple-iphone-15-128-gb-black/600000000",
                "deliveryEta": "3-4 Days",
                "inStock": True
            },
            {
                "platformName": "Blinkit",
                "price": 74900,
                "originalPrice": 79900,
                "rating": 4.8,
                "deliveryEta": "12 mins",
                "imageUrl": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://blinkit.com/prn/apple-iphone-15-128gb/prid/58912",
                "inStock": True
            }
        ]
    },
    {
        "id": "sony-wh-1000xm5-headphones",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "category": "Electronics",
        "description": "Industry-leading noise canceling with 8 microphones, 30 hours battery life, and crystal clear hands-free calling.",
        "mainImage": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
        "platforms": [
            {
                "platformName": "Amazon",
                "price": 26990,
                "originalPrice": 34990,
                "rating": 4.5,
                "reviewCount": 3120,
                "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.amazon.in/dp/B0B56769VT",
                "deliveryEta": "Same Day Delivery",
                "inStock": True
            },
            {
                "platformName": "Flipkart",
                "price": 27990,
                "originalPrice": 34990,
                "rating": 4.4,
                "reviewCount": 1450,
                "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.flipkart.com/sony-wh-1000xm5/p/itm123456789",
                "deliveryEta": "2 Days",
                "inStock": True
            },
            {
                "platformName": "Flipkart Minutes",
                "price": 28490,
                "originalPrice": 34990,
                "rating": 4.6,
                "deliveryEta": "15 mins",
                "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.flipkart.com/minutes",
                "inStock": True
            }
        ]
    },
    {
        "id": "amul-taaza-toned-milk-1l",
        "name": "Amul Taaza Toned Milk - 1 Litre Pouch",
        "category": "Groceries",
        "description": "Pasteurised toned milk with 3% fat and 8.5% SNF. Fresh, nutrient-dense daily milk pouch.",
        "mainImage": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=600&auto=format&fit=crop&q=80",
        "platforms": [
            {
                "platformName": "Blinkit",
                "price": 54,
                "originalPrice": 54,
                "rating": 4.9,
                "deliveryEta": "10 mins",
                "imageUrl": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://blinkit.com/prn/amul-taaza-toned-milk-1l/prid/123",
                "inStock": True
            },
            {
                "platformName": "Zepto",
                "price": 54,
                "originalPrice": 54,
                "rating": 4.8,
                "deliveryEta": "8 mins",
                "imageUrl": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://zepto.com/product/amul-taaza-toned-milk-1l",
                "inStock": True
            },
            {
                "platformName": "Swiggy Instamart",
                "price": 55,
                "originalPrice": 55,
                "rating": 4.7,
                "deliveryEta": "14 mins",
                "imageUrl": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.swiggy.com/instamart/item/amul-taaza-toned-milk",
                "inStock": True
            }
        ]
    },
    {
        "id": "nike-air-force-1-07-white",
        "name": "Nike Air Force 1 '07 Sneakers - Triple White",
        "category": "Fashion",
        "description": "Legendary style with crisp leather, bold details, and stitched overlays for iconic daily wear.",
        "mainImage": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80",
        "platforms": [
            {
                "platformName": "Myntra",
                "price": 7495,
                "originalPrice": 8995,
                "rating": 4.6,
                "reviewCount": 1820,
                "imageUrl": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.myntra.com/casual-shoes/nike/nike-men-white-air-force-1-07-sneakers/123456",
                "deliveryEta": "3 Days",
                "inStock": True
            },
            {
                "platformName": "Amazon",
                "price": 7995,
                "originalPrice": 8995,
                "rating": 4.4,
                "reviewCount": 940,
                "imageUrl": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.amazon.in/dp/B08N5N6N7P",
                "deliveryEta": "Tomorrow",
                "inStock": True
            },
            {
                "platformName": "Nykaa",
                "price": 8495,
                "originalPrice": 8995,
                "rating": 4.7,
                "reviewCount": 310,
                "imageUrl": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=300&auto=format&fit=crop&q=80",
                "deeplink": "https://www.nykaa.com/nike-air-force-1",
                "deliveryEta": "2-4 Days",
                "inStock": True
            }
        ]
    }
]

# Normalizes raw QuickCommerce platform item dictionary into standardized Platform schema
def normalize_platform_data(platform_dict: Dict[str, Any]) -> Platform:
    return Platform(
        platformName=platform_dict.get("platformName", "Unknown Platform"),
        price=float(platform_dict.get("price", 0.0)),
        originalPrice=float(platform_dict["originalPrice"]) if platform_dict.get("originalPrice") else None,
        rating=float(platform_dict.get("rating", 0.0)),
        reviewCount=int(platform_dict["reviewCount"]) if platform_dict.get("reviewCount") is not None else None,
        imageUrl=platform_dict.get("imageUrl", ""),
        deeplink=platform_dict.get("deeplink", "#"),
        deliveryEta=platform_dict.get("deliveryEta"),
        inStock=bool(platform_dict.get("inStock", True)),
        computedScore=platform_dict.get("computedScore")
    )

# Normalizes raw QuickCommerce API product payload into standard Product Pydantic model
def normalize_product_data(raw_data: Dict[str, Any]) -> Product:
    platforms_raw = raw_data.get("platforms", [])
    normalized_platforms = [normalize_platform_data(p) for p in platforms_raw]
    return Product(
        id=str(raw_data.get("id", "")),
        name=str(raw_data.get("name", "Unnamed Product")),
        category=str(raw_data.get("category", "General")),
        description=raw_data.get("description"),
        mainImage=str(raw_data.get("mainImage", "")),
        platforms=normalized_platforms,
        bestPickPlatform=raw_data.get("bestPickPlatform")
    )

# Fetches product listings from QuickCommerce API with graceful error handling and fallback
async def fetch_products_from_quickcommerce(query: Optional[str] = None) -> List[Product]:
    headers = {
        "x-api-key": QUICKCOMMERCE_API_KEY,
        "Authorization": f"Bearer {QUICKCOMMERCE_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            url = f"{QUICKCOMMERCE_BASE_URL}/products/search"
            params = {"q": query} if query else {}
            response = await client.get(url, headers=headers, params=params)

            # If external API returns successful response, normalize real live data
            if response.status_code == 200:
                data = response.json()
                raw_items = data.get("products", data if isinstance(data, list) else [])
                return [normalize_product_data(item) for item in raw_items]
            else:
                logger.warning(f"QuickCommerce API returned status {response.status_code}. Using fallback dataset.")
    except Exception as e:
        logger.error(f"Failed to connect to QuickCommerce API: {e}. Utilizing graceful fallback dataset.")

    # Graceful fallback filtering using local matching products
    matched = FALLBACK_PRODUCTS
    if query and query.strip():
        q = query.lower().strip()
        matched = [
            p for p in FALLBACK_PRODUCTS
            if q in p["name"].lower()
            or q in p["category"].lower()
            or (p.get("description") and q in p["description"].lower())
            or any(q in pl["platformName"].lower() for pl in p.get("platforms", []))
        ]

    return [normalize_product_data(p) for p in matched]

# Fetches a single product by its unique identifier with graceful fallback
async def fetch_product_by_id(product_id: str) -> Optional[Product]:
    all_products = await fetch_products_from_quickcommerce()
    for prod in all_products:
        if prod.id == product_id:
            return prod
    return None
