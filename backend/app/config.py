# Loads environment variables and defines all application configuration constants
import os
from dotenv import load_dotenv

# Loads variables from the local .env file into the runtime environment
load_dotenv()

# QuickCommerce API credentials loaded from environment variables (never hardcoded)
QUICKCOMMERCE_API_KEY: str = os.getenv("QUICKCOMMERCE_API_KEY", "")
QUICKCOMMERCE_BASE_URL: str = os.getenv("QUICKCOMMERCE_BASE_URL", "https://api.quickcommerce.io/v1")

# BrightData API credentials for e-commerce search and live price scraping
BRIGHTDATA_API_KEY: str = os.getenv("BRIGHTDATA_API_KEY", "c976a32d-f2c0-4e39-97ff-5e7e4761a4d9")
BRIGHTDATA_BASE_URL: str = os.getenv("BRIGHTDATA_BASE_URL", "https://api.brightdata.com")

# Server configuration
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# SQLite database file path — stored inside backend/ directory
DATABASE_PATH: str = os.getenv("DATABASE_PATH", "comparo_cache.db")

# ── Cache Freshness Settings ──────────────────────────────────────────────────
# Data younger than 24h is considered fresh — no API call needed
FRESH_CACHE_HOURS: int = int(os.getenv("FRESH_CACHE_HOURS", "24"))

# Data between 24–72h is stale — return it now, refresh in background
STALE_CACHE_HOURS: int = int(os.getenv("STALE_CACHE_HOURS", "72"))

# Trending products refresh interval in hours (every 48h is enough for trending)
TRENDING_REFRESH_HOURS: int = int(os.getenv("TRENDING_REFRESH_HOURS", "48"))

# ── API Budget Settings ───────────────────────────────────────────────────────
# Hard limit on QuickCommerce API calls per calendar month
MONTHLY_API_LIMIT: int = int(os.getenv("MONTHLY_API_LIMIT", "50"))

# Per-feature budget split — must sum to <= MONTHLY_API_LIMIT
CATALOG_BUDGET: int = int(os.getenv("CATALOG_BUDGET", "20"))    # home/all-products refresh
SEARCH_BUDGET: int = int(os.getenv("SEARCH_BUDGET", "15"))      # user search queries
TRENDING_BUDGET: int = int(os.getenv("TRENDING_BUDGET", "10"))  # trending section refresh
EMERGENCY_BUDGET: int = int(os.getenv("EMERGENCY_BUDGET", "5")) # reserve buffer
