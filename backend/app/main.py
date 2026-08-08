# FastAPI application entry point and global server setup
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.product_routes import router as product_router

# Initializes the FastAPI application with metadata
app = FastAPI(
    title="Comparo - QuickCommerce Price Comparison API",
    description="Backend service providing real-time product price comparison and best deal recommendations.",
    version="1.0.0"
)

# Configures CORS middleware to allow cross-origin requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registers product endpoints for search and comparison features
app.include_router(product_router)

# Confirms QuickCommerce API Key loading from .env upon server startup
@app.on_event("startup")
async def startup_event():
    from app.config import QUICKCOMMERCE_API_KEY
    if QUICKCOMMERCE_API_KEY:
        masked = QUICKCOMMERCE_API_KEY[:8] + "..." + QUICKCOMMERCE_API_KEY[-4:]
        print(f"[Startup] QuickCommerce API Key loaded successfully from .env: {masked}")
    else:
        print("[Startup] WARNING: QUICKCOMMERCE_API_KEY is missing in .env configuration!")

# Root endpoint providing health check status and interactive API documentation link
@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Comparo API",
        "documentation": "/docs",
        "endpoints": {
            "search": "/search?query={product_name}",
            "compare": "/compare/{product_id}"
        }
    }
