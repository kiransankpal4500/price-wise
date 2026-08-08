# Loads environment variables from .env file for easy configuration management
import os
from dotenv import load_dotenv

# Loads variables from the local .env file into the runtime environment
load_dotenv()

# Retrieves the QuickCommerce API key used for authenticating external requests
QUICKCOMMERCE_API_KEY: str = os.getenv("QUICKCOMMERCE_API_KEY", "")

# Base URL for QuickCommerce API service endpoints
QUICKCOMMERCE_BASE_URL: str = os.getenv("QUICKCOMMERCE_BASE_URL", "https://api.quickcommerce.io/v1")

# Default server host and port configurations
HOST: str = os.getenv("HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "8000"))
