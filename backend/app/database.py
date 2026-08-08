# Database module — creates and manages the SQLite database connection, table schema, and rich seed library
import sqlite3
import aiosqlite
import logging
import json
from datetime import datetime, timezone, timedelta
from app.config import DATABASE_PATH

logger = logging.getLogger(__name__)

# SQL to create cached_products table — stores one row per product+platform combination
CREATE_CACHED_PRODUCTS_TABLE = """
CREATE TABLE IF NOT EXISTS cached_products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    name TEXT,
    brand TEXT,
    category TEXT,
    image_url TEXT,
    product_url TEXT,
    price REAL,
    original_price REAL,
    discount REAL,
    rating REAL,
    review_count INTEGER,
    availability BOOLEAN DEFAULT 1,
    delivery_info TEXT,
    description TEXT,
    raw_api_data TEXT,
    search_key TEXT,
    fetched_at TEXT,
    expires_at TEXT,
    updated_at TEXT,
    UNIQUE(product_id, platform) ON CONFLICT REPLACE
);
"""

# SQL to create api_usage table — tracks monthly call count with one row per month
CREATE_API_USAGE_TABLE = """
CREATE TABLE IF NOT EXISTS api_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    month TEXT NOT NULL UNIQUE,
    api_calls INTEGER DEFAULT 0,
    last_call_at TEXT,
    updated_at TEXT
);
"""

CREATE_SEARCH_INDEX = """
CREATE INDEX IF NOT EXISTS idx_cached_products_search_key
ON cached_products(search_key);
"""

CREATE_PRODUCT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_cached_products_product_id
ON cached_products(product_id);
"""

# Full product library covering Electronics, Fashion, Grocery, Home, Sports, Beauty across platforms
SEED_PRODUCTS = [
    {
        "id": "apple-iphone-15-128gb",
        "name": "Apple iPhone 15 (128 GB) - Black",
        "category": "Electronics",
        "description": "Dynamic Island, 48MP Main Camera with 2x Telephoto, Super Retina XDR Display, and A16 Bionic chip.",
        "search_keys": ["__trending__", "iphone", "iphone 15", "apple", "phone", "mobile"],
        "platforms": [
            {
                "platform": "Amazon",
                "price": 71290,
                "original_price": 79900,
                "rating": 4.6,
                "review_count": 4520,
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in/dp/B0CHX1W1XY",
                "delivery_info": "Tomorrow, by 10 PM",
                "availability": 1,
            },
            {
                "platform": "Flipkart",
                "price": 69999,
                "original_price": 79900,
                "rating": 4.7,
                "review_count": 8930,
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Blinkit",
                "price": 74900,
                "original_price": 79900,
                "rating": 4.8,
                "review_count": 120,
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://blinkit.com/prn/apple-iphone-15-128gb/prid/58912",
                "delivery_info": "12 mins",
                "availability": 1,
            },
            {
                "platform": "JioMart",
                "price": 72490,
                "original_price": 79900,
                "rating": 4.3,
                "review_count": 410,
                "image_url": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.jiomart.com",
                "delivery_info": "3 Days",
                "availability": 1,
            },
        ],
    },
    {
        "id": "sony-wh-1000xm5-headphones",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "category": "Electronics",
        "description": "Industry-leading noise canceling with 8 microphones, 30 hours battery life, and crystal clear hands-free calling.",
        "search_keys": ["__trending__", "sony", "headphones", "sony headphones", "audio"],
        "platforms": [
            {
                "platform": "Amazon",
                "price": 26990,
                "original_price": 34990,
                "rating": 4.5,
                "review_count": 3120,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in/dp/B0B56769VT",
                "delivery_info": "Same Day Delivery",
                "availability": 1,
            },
            {
                "platform": "Flipkart",
                "price": 27990,
                "original_price": 34990,
                "rating": 4.4,
                "review_count": 1450,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.flipkart.com",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Zepto",
                "price": 28490,
                "original_price": 34990,
                "rating": 4.6,
                "review_count": 85,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.zeptonow.com",
                "delivery_info": "10 mins",
                "availability": 1,
            },
        ],
    },
    {
        "id": "apple-macbook-air-m2",
        "name": "Apple MacBook Air M2 (13.6-inch, 8GB RAM, 256GB SSD) - Starlight",
        "category": "Electronics",
        "description": "Supercharged by M2 chip, 13.6-inch Liquid Retina Display, 1080p FaceTime HD Camera, and up to 18 hours battery life.",
        "search_keys": ["macbook", "macbook air", "laptop", "apple laptop"],
        "platforms": [
            {
                "platform": "Amazon",
                "price": 94990,
                "original_price": 114900,
                "rating": 4.7,
                "review_count": 2890,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow, by 10 PM",
                "availability": 1,
            },
            {
                "platform": "Flipkart",
                "price": 93990,
                "original_price": 114900,
                "rating": 4.8,
                "review_count": 5120,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.flipkart.com",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Reliance Digital",
                "price": 95900,
                "original_price": 114900,
                "rating": 4.6,
                "review_count": 340,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.reliancedigital.in",
                "delivery_info": "Store Pickup Available",
                "availability": 1,
            },
        ],
    },
    {
        "id": "amul-taaza-toned-milk-1l",
        "name": "Amul Taaza Toned Milk (1 Litre)",
        "category": "Grocery",
        "description": "Pasteurised toned milk with 3.0% fat content. Fresh daily delivery.",
        "search_keys": ["__trending__", "milk", "amul milk", "amul", "grocery", "taaza milk"],
        "platforms": [
            {
                "platform": "Blinkit",
                "price": 54,
                "original_price": 56,
                "rating": 4.9,
                "review_count": 14200,
                "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://blinkit.com",
                "delivery_info": "8 mins",
                "availability": 1,
            },
            {
                "platform": "Zepto",
                "price": 54,
                "original_price": 56,
                "rating": 4.8,
                "review_count": 9800,
                "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.zeptonow.com",
                "delivery_info": "10 mins",
                "availability": 1,
            },
            {
                "platform": "Swiggy Instamart",
                "price": 55,
                "original_price": 56,
                "rating": 4.7,
                "review_count": 5600,
                "image_url": "https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.swiggy.com/instamart",
                "delivery_info": "12 mins",
                "availability": 1,
            },
        ],
    },
    {
        "id": "nescafe-classic-instant-coffee-200g",
        "name": "Nescafe Classic 100% Pure Instant Coffee (200g Jar)",
        "category": "Grocery",
        "description": "Rich roasted coffee aroma with smooth taste. Made from 100% pure Robusta coffee beans.",
        "search_keys": ["coffee", "nescafe coffee", "nescafe", "instant coffee", "grocery"],
        "platforms": [
            {
                "platform": "Blinkit",
                "price": 585,
                "original_price": 650,
                "rating": 4.8,
                "review_count": 6400,
                "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://blinkit.com",
                "delivery_info": "10 mins",
                "availability": 1,
            },
            {
                "platform": "Amazon Fresh",
                "price": 569,
                "original_price": 650,
                "rating": 4.6,
                "review_count": 12400,
                "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow Morning",
                "availability": 1,
            },
            {
                "platform": "Zepto",
                "price": 590,
                "original_price": 650,
                "rating": 4.7,
                "review_count": 4200,
                "image_url": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.zeptonow.com",
                "delivery_info": "12 mins",
                "availability": 1,
            },
        ],
    },
    {
        "id": "nike-air-jordan-1-retro-high",
        "name": "Nike Air Jordan 1 Retro High OG - Chicago",
        "category": "Fashion",
        "description": "Iconic high-top sneaker with premium leather upper and encapsulated Air-Sole unit.",
        "search_keys": ["__trending__", "nike", "nike shoes", "shoes", "jordan", "air jordan", "sneakers"],
        "platforms": [
            {
                "platform": "Nike Store",
                "price": 16995,
                "original_price": 18995,
                "rating": 4.9,
                "review_count": 2100,
                "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.nike.com/in/",
                "delivery_info": "3-5 Days",
                "availability": 1,
            },
            {
                "platform": "Myntra",
                "price": 15499,
                "original_price": 18995,
                "rating": 4.8,
                "review_count": 1450,
                "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.myntra.com",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Amazon",
                "price": 17490,
                "original_price": 18995,
                "rating": 4.6,
                "review_count": 520,
                "image_url": "https://images.unsplash.com/photo-1552346154-21d32810aba3?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow",
                "availability": 1,
            },
        ],
    },
    {
        "id": "levis-501-original-fit-jeans",
        "name": "Levi's 501 Original Fit Stretch Jeans - Dark Indigo",
        "category": "Fashion",
        "description": "The original blue jean with straight leg fit, iconic button fly, and 100% cotton denim.",
        "search_keys": ["levi's jeans", "levis", "jeans", "denim", "fashion"],
        "platforms": [
            {
                "platform": "Myntra",
                "price": 3199,
                "original_price": 4299,
                "rating": 4.7,
                "review_count": 3400,
                "image_url": "https://images.unsplash.com/photo-1542272604-780c36856d67?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.myntra.com",
                "delivery_info": "Tomorrow",
                "availability": 1,
            },
            {
                "platform": "Amazon",
                "price": 3439,
                "original_price": 4299,
                "rating": 4.5,
                "review_count": 1890,
                "image_url": "https://images.unsplash.com/photo-1542272604-780c36856d67?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Tata CLiQ",
                "price": 3299,
                "original_price": 4299,
                "rating": 4.6,
                "review_count": 620,
                "image_url": "https://images.unsplash.com/photo-1542272604-780c36856d67?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.tatacliq.com",
                "delivery_info": "3 Days",
                "availability": 1,
            },
        ],
    },
    {
        "id": "maybelline-fit-me-foundation",
        "name": "Maybelline New York Fit Me Matte + Poreless Foundation (30ml)",
        "category": "Beauty",
        "description": "Oil-free matte foundation with clay technology to control shine and refine pores.",
        "search_keys": ["maybelline", "foundation", "makeup", "beauty"],
        "platforms": [
            {
                "platform": "Nykaa",
                "price": 489,
                "original_price": 649,
                "rating": 4.8,
                "review_count": 28400,
                "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.nykaa.com",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Blinkit",
                "price": 519,
                "original_price": 649,
                "rating": 4.7,
                "review_count": 3200,
                "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://blinkit.com",
                "delivery_info": "10 mins",
                "availability": 1,
            },
            {
                "platform": "Amazon",
                "price": 479,
                "original_price": 649,
                "rating": 4.5,
                "review_count": 14200,
                "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow",
                "availability": 1,
            },
        ],
    },
    {
        "id": "philips-digital-air-fryer-hd9200",
        "name": "Philips Digital Air Fryer HD9200/90 (4.1 Litre, 1400W)",
        "category": "Home",
        "description": "Rapid Air Technology uses hot air to cook healthy meals with up to 90% less fat.",
        "search_keys": ["air fryer", "philips air fryer", "fryer", "kitchen", "home"],
        "platforms": [
            {
                "platform": "Amazon",
                "price": 6799,
                "original_price": 9995,
                "rating": 4.6,
                "review_count": 8900,
                "image_url": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow",
                "availability": 1,
            },
            {
                "platform": "Flipkart",
                "price": 6690,
                "original_price": 9995,
                "rating": 4.7,
                "review_count": 4500,
                "image_url": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.flipkart.com",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Croma",
                "price": 6990,
                "original_price": 9995,
                "rating": 4.5,
                "review_count": 920,
                "image_url": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.croma.com",
                "delivery_info": "Same Day Pickup",
                "availability": 1,
            },
        ],
    },
    {
        "id": "decathlon-yoga-mat-8mm",
        "name": "Decathlon Nyamba Anti-Slip Yoga Mat (8mm Thick)",
        "category": "Sports",
        "description": "Cushioned 8mm high-density foam mat with alignment lines and carry strap.",
        "search_keys": ["yoga mat", "decathlon", "fitness", "sports", "mat"],
        "platforms": [
            {
                "platform": "Decathlon",
                "price": 1299,
                "original_price": 1499,
                "rating": 4.8,
                "review_count": 6200,
                "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.decathlon.in",
                "delivery_info": "2 Days",
                "availability": 1,
            },
            {
                "platform": "Amazon",
                "price": 1349,
                "original_price": 1499,
                "rating": 4.6,
                "review_count": 2100,
                "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://www.amazon.in",
                "delivery_info": "Tomorrow",
                "availability": 1,
            },
            {
                "platform": "Blinkit",
                "price": 1399,
                "original_price": 1499,
                "rating": 4.7,
                "review_count": 410,
                "image_url": "https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400&auto=format&fit=crop&q=80",
                "product_url": "https://blinkit.com",
                "delivery_info": "15 mins",
                "availability": 1,
            },
        ],
    },
]


def init_db_sync() -> None:
    """Synchronously initialises the SQLite database, creates tables, and seeds full product library."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(CREATE_CACHED_PRODUCTS_TABLE)
        cursor.execute(CREATE_API_USAGE_TABLE)
        cursor.execute(CREATE_SEARCH_INDEX)
        cursor.execute(CREATE_PRODUCT_INDEX)
        conn.commit()

        logger.info("[DB] Upserting full product library into database cache...")
        now = datetime.now(timezone.utc).isoformat()
        expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

        inserted_count = 0
        for item in SEED_PRODUCTS:
            search_keys = item.get("search_keys", ["__trending__"])
            for skey in search_keys:
                for pl in item["platforms"]:
                    raw_blob = json.dumps({
                        "product_id": item["id"],
                        "name": item["name"],
                        "category": item["category"],
                        "platform": pl["platform"],
                        "price": pl["price"],
                    })
                    cursor.execute(
                        """
                        INSERT OR REPLACE INTO cached_products (
                            product_id, platform, name, category, description,
                            image_url, product_url, price, original_price, discount,
                            rating, review_count, availability, delivery_info,
                            raw_api_data, search_key, fetched_at, expires_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            item["id"],
                            pl["platform"],
                            item["name"],
                            item["category"],
                            item["description"],
                            pl["image_url"],
                            pl["product_url"],
                            pl["price"],
                            pl.get("original_price"),
                            None,
                            pl["rating"],
                            pl.get("review_count"),
                            pl.get("availability", 1),
                            pl.get("delivery_info"),
                            raw_blob,
                            skey,
                            now,
                            expires_at,
                            now,
                        ),
                    )
                    inserted_count += 1

        conn.commit()
        conn.close()
        logger.info(f"[DB] Successfully synced product library ({inserted_count} rows) at: {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"[DB] Failed to initialise database: {e}")
        raise


async def get_db() -> aiosqlite.Connection:
    """Returns an async SQLite connection. Caller is responsible for closing it."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db
