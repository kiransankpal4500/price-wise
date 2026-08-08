# Database module — creates and manages the SQLite database connection and table schema
import sqlite3
import aiosqlite
import logging
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

# Creates index on search_key for fast search lookups
CREATE_SEARCH_INDEX = """
CREATE INDEX IF NOT EXISTS idx_cached_products_search_key
ON cached_products(search_key);
"""

# Creates index on product_id for fast product detail lookups
CREATE_PRODUCT_INDEX = """
CREATE INDEX IF NOT EXISTS idx_cached_products_product_id
ON cached_products(product_id);
"""


def init_db_sync() -> None:
    """Synchronously initialises the SQLite database and creates tables on startup."""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute(CREATE_CACHED_PRODUCTS_TABLE)
        cursor.execute(CREATE_API_USAGE_TABLE)
        cursor.execute(CREATE_SEARCH_INDEX)
        cursor.execute(CREATE_PRODUCT_INDEX)
        conn.commit()
        conn.close()
        logger.info(f"[DB] Database initialised at: {DATABASE_PATH}")
    except Exception as e:
        logger.error(f"[DB] Failed to initialise database: {e}")
        raise


async def get_db() -> aiosqlite.Connection:
    """Returns an async SQLite connection. Caller is responsible for closing it."""
    db = await aiosqlite.connect(DATABASE_PATH)
    # Return rows as dicts for easy access by column name
    db.row_factory = aiosqlite.Row
    return db
