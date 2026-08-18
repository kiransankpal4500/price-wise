# Loads environment variables and defines all application configuration constants
import os
from dotenv import load_dotenv

# Loads variables from the local .env file into the runtime environment
load_dotenv()

# QuickCommerce API credentials loaded from environment variables
QUICKCOMMERCE_API_KEY: str = os.getenv("QUICKCOMMERCE_API_KEY", "f009f00b-ce0d-4170-b5fe-adeaee1099d0")
QUICKCOMMERCE_BASE_URL: str = os.getenv(
    "QUICKCOMMERCE_BASE_URL",
    os.getenv("QUICKCOMMERCE_API_BASE_URL", "https://api.quickcommerceapi.com/v1")
)

# Default location coordinates (Mumbai, India) for location-based QuickCommerce search
DEFAULT_LAT: str = os.getenv("DEFAULT_LAT", "19.0760")
DEFAULT_LON: str = os.getenv("DEFAULT_LON", "72.8777")

# BrightData API credentials for e-commerce search and live price scraping
BRIGHTDATA_API_KEY: str = os.getenv("BRIGHTDATA_API_KEY", "c976a32d-f2c0-4e39-97ff-5e7e4761a4d9")
BRIGHTDATA_BASE_URL: str = os.getenv("BRIGHTDATA_BASE_URL", "https://api.brightdata.com")

# Server configuration
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))

# SQLite database file path — stored inside backend/ directory or /tmp for Vercel serverless
DATABASE_PATH: str = os.getenv(
    "DATABASE_PATH",
    "/tmp/comparo_cache.db" if os.getenv("VERCEL") else "comparo_cache.db"
)

# ── Cache Freshness Settings ──────────────────────────────────────────────────
# Cache TTL in minutes for search queries (default 30 minutes)
CACHE_TTL_MINUTES: int = int(os.getenv("CACHE_TTL_MINUTES", "30"))

# Data younger than 24h is considered fresh — no API call needed
FRESH_CACHE_HOURS: int = int(os.getenv("FRESH_CACHE_HOURS", "24"))

# Data between 24–72h is stale — return it now, refresh in background
STALE_CACHE_HOURS: int = int(os.getenv("STALE_CACHE_HOURS", "72"))

# Trending products refresh interval in hours (every 48h is enough for trending)
TRENDING_REFRESH_HOURS: int = int(os.getenv("TRENDING_REFRESH_HOURS", "48"))

# ── Scraper Settings ───────────────────────────────────────────────────────────
ENABLE_PLAYWRIGHT_FALLBACK: bool = os.getenv("ENABLE_PLAYWRIGHT_FALLBACK", "true").lower() == "true"
ENABLE_BRIGHTDATA_FALLBACK: bool = os.getenv("ENABLE_BRIGHTDATA_FALLBACK", "true").lower() == "true"
ENABLE_APIFY_FALLBACK: bool = os.getenv("ENABLE_APIFY_FALLBACK", "true").lower() == "true"
APIFY_API_KEY: str = os.getenv("APIFY_API_KEY", "")

# Maximum pages to scrape per search request per source (default: 3)
MAX_PAGES_PER_SOURCE: int = int(os.getenv("MAX_PAGES_PER_SOURCE", "3"))

# Maximum products to collect per source per query (default: 100)
MAX_PRODUCTS_PER_SOURCE: int = int(os.getenv("MAX_PRODUCTS_PER_SOURCE", "100"))


# ── API Budget Settings ───────────────────────────────────────────────────────
# Hard limit on QuickCommerce API calls per calendar month
MONTHLY_API_LIMIT: int = int(os.getenv("MONTHLY_API_LIMIT", "50"))

# Per-feature budget split — must sum to <= MONTHLY_API_LIMIT
CATALOG_BUDGET: int = int(os.getenv("CATALOG_BUDGET", "20"))    # home/all-products refresh
SEARCH_BUDGET: int = int(os.getenv("SEARCH_BUDGET", "15"))      # user search queries
TRENDING_BUDGET: int = int(os.getenv("TRENDING_BUDGET", "10"))  # trending section refresh
EMERGENCY_BUDGET: int = int(os.getenv("EMERGENCY_BUDGET", "5")) # reserve buffer

