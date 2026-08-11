import sys
import os

# Add api directory to sys.path so 'app' can be imported directly
api_dir = os.path.dirname(__file__)
if api_dir not in sys.path:
    sys.path.insert(0, api_dir)

# Enforce /tmp DB path on Vercel
if os.getenv("VERCEL") or os.environ.get("VERCEL"):
    os.environ["DATABASE_PATH"] = "/tmp/comparo_cache.db"

# Initialize SQLite database and seed catalog on serverless cold start
try:
    from app.database import init_db_sync
    init_db_sync()
except Exception as e:
    print(f"[Vercel Serverless] DB startup warning: {e}")

from app.main import app
