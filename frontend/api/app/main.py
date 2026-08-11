# FastAPI application entry point — initialises DB on startup and registers all routes
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.product_routes import router as product_router
from app.database import init_db_sync

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Initialises the FastAPI application with metadata
app = FastAPI(
    title="Comparo - QuickCommerce Price Comparison API",
    description=(
        "Backend service providing real-time product price comparison "
        "and best deal recommendations. Uses a smart 50-call/month cache "
        "to protect the QuickCommerce API quota."
    ),
    version="2.0.0",
)

# Configures CORS middleware to allow cross-origin requests from the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registers product endpoints (search, trending, compare, system/api-usage)
app.include_router(product_router)


# Runs on server startup — creates SQLite DB tables and confirms API key is loaded
@app.on_event("startup")
async def startup_event():
    # Initialise the SQLite database (creates tables if they don't exist)
    init_db_sync()

    # Confirm QuickCommerce API key is loaded from .env (never log the full key)
    from app.config import QUICKCOMMERCE_API_KEY
    if QUICKCOMMERCE_API_KEY:
        masked = QUICKCOMMERCE_API_KEY[:8] + "..." + QUICKCOMMERCE_API_KEY[-4:]
        logger.info(f"[Startup] QuickCommerce API Key loaded: {masked}")
    else:
        logger.warning("[Startup] WARNING: QUICKCOMMERCE_API_KEY is missing in .env!")

    logger.info("[Startup] Comparo backend ready. Cache-first architecture active.")


# Root health-check endpoint
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Comparo API",
        "version": "2.0.0",
        "architecture": "cache-first (50 calls/month budget)",
        "documentation": "/docs",
        "endpoints": {
            "search": "/search?query={product_name}",
            "trending": "/trending",
            "compare": "/compare/{product_id}",
            "api_usage": "/api/system/api-usage",
        },
    }
