import sys
import os

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

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
