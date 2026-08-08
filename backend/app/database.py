# Database module — creates and manages the SQLite database connection, table schema, and seed data
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

# Initial seed data for trending and catalog items to ensure database is never empty
SEED_PRODUCTS = [
    {
        "id": "apple-iphone-15-128gb",
        "name": "Apple iPhone 15 (128 GB) - Black",
        "category": "Electronics",
        "description": "Dynamic Island, 48MP Main Camera with 2x Telephoto, Super Retina XDR Display, and A16 Bionic chip.",
        "search_key": "__trending__",
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
        ],
    },
    {
        "id": "sony-wh-1000xm5-headphones",
        "name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "category": "Electronics",
        "description": "Industry-leading noise canceling with 8 microphones, 30 hours battery life, and crystal clear hands-free calling.",
        "search_key": "__trending__",
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
                "product_url": "https://www.flipkart.com/sony-wh-1000xm5/p/itm123456789",
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
        "id": "amul-taaza-toned-milk-1l",
        "name": "Amul Taaza Toned Milk (1 Litre)",
        "category": "Grocery",
        "description": "Pasteurised toned milk with 3.0% fat content. Fresh daily delivery.",
        "search_key": "__trending__",
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
        "id": "nike-air-jordan-1-retro-high",
        "name": "Nike Air Jordan 1 Retro High OG - Chicago",
        "category": "Fashion",
        "description": "Iconic high-top sneaker with premium leather upper and encapsulated Air-Sole unit.",
        "search_key": "__trending__",
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
]


def init_db_sync() -> None:
    """Synchronously initialises the SQLite database, creates tables, and seeds initial products."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(CREATE_CACHED_PRODUCTS_TABLE)
        cursor.execute(CREATE_API_USAGE_TABLE)
        cursor.execute(CREATE_SEARCH_INDEX)
        cursor.execute(CREATE_PRODUCT_INDEX)
        conn.commit()

        # Check if cached_products table is empty
        cursor.execute("SELECT COUNT(*) FROM cached_products")
        count = cursor.fetchone()[0]

        if count == 0:
            logger.info("[DB] Table cached_products is empty. Seeding initial product catalog...")
            now = datetime.now(timezone.utc).isoformat()
            expires_at = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

            for item in SEED_PRODUCTS:
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
                            item["search_key"],
                            now,
                            expires_at,
                            now,
                        ),
                    )
            conn.commit()
            logger.info(f"[DB] Successfully seeded {len(SEED_PRODUCTS)} initial product catalog items.")

        conn.close()
        logger.info(f"[DB] Database initialised at: {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"[DB] Failed to initialise database: {e}")
        raise


async def get_db() -> aiosqlite.Connection:
    """Returns an async SQLite connection. Caller is responsible for closing it."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db
