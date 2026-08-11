# API budget enforcement module — tracks and limits QuickCommerce API calls to 50 per month
import logging
from datetime import datetime, timezone
from typing import Optional
from app.database import get_db
from app.config import (
    MONTHLY_API_LIMIT,
    CATALOG_BUDGET,
    SEARCH_BUDGET,
    TRENDING_BUDGET,
    EMERGENCY_BUDGET,
)

logger = logging.getLogger(__name__)

# Budget type labels — used to enforce per-feature call limits
BUDGET_CATALOG = "CATALOG"
BUDGET_SEARCH = "SEARCH"
BUDGET_TRENDING = "TRENDING"
BUDGET_EMERGENCY = "EMERGENCY"

# Maps budget types to their allowed monthly call counts
BUDGET_LIMITS = {
    BUDGET_CATALOG: CATALOG_BUDGET,
    BUDGET_SEARCH: SEARCH_BUDGET,
    BUDGET_TRENDING: TRENDING_BUDGET,
    BUDGET_EMERGENCY: EMERGENCY_BUDGET,
}


def _current_month() -> str:
    """Returns the current year-month as a string key e.g. '2026-08'."""
    return datetime.now(timezone.utc).strftime("%Y-%m")


async def get_monthly_usage() -> dict:
    """
    Reads the current month's API usage from the database.
    Returns dict with api_calls count, last_call_at, and monthly_limit.
    """
    month = _current_month()
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT api_calls, last_call_at FROM api_usage WHERE month = ?", (month,)
        )
        row = await cursor.fetchone()
        calls = row["api_calls"] if row else 0
        last_call = row["last_call_at"] if row else None
        return {
            "month": month,
            "api_calls": calls,
            "last_call_at": last_call,
            "monthly_limit": MONTHLY_API_LIMIT,
            "calls_remaining": max(0, MONTHLY_API_LIMIT - calls),
        }
    finally:
        await db.close()


async def can_make_api_call(budget_type: str = BUDGET_CATALOG) -> bool:
    """
    Checks whether an API call is permitted based on monthly total and per-feature budget.
    Returns False if the monthly limit or type-specific budget would be exceeded.
    """
    usage = await get_monthly_usage()
    total_calls = usage["api_calls"]

    # Hard stop at overall monthly limit
    if total_calls >= MONTHLY_API_LIMIT:
        logger.warning(
            f"[Budget] HARD LIMIT reached: {total_calls}/{MONTHLY_API_LIMIT} calls used this month."
        )
        return False

    # Per-feature budget is advisory — prevents one feature consuming all calls
    type_limit = BUDGET_LIMITS.get(budget_type, EMERGENCY_BUDGET)
    if total_calls >= type_limit:
        logger.info(
            f"[Budget] {budget_type} budget ({type_limit}) reached. "
            f"Total used: {total_calls}/{MONTHLY_API_LIMIT}."
        )
        # Still allow call if overall quota has room — emergency override
        if total_calls >= MONTHLY_API_LIMIT - EMERGENCY_BUDGET:
            return False

    return True


async def increment_api_call() -> int:
    """
    Atomically increments the monthly API call count after a successful API request.
    Returns the new total call count.
    """
    month = _current_month()
    now = datetime.now(timezone.utc).isoformat()
    db = await get_db()
    try:
        # Use INSERT OR REPLACE with atomic increment to prevent race conditions
        await db.execute(
            """
            INSERT INTO api_usage (month, api_calls, last_call_at, updated_at)
            VALUES (?, 1, ?, ?)
            ON CONFLICT(month) DO UPDATE SET
                api_calls = api_calls + 1,
                last_call_at = excluded.last_call_at,
                updated_at = excluded.updated_at
            """,
            (month, now, now),
        )
        await db.commit()

        # Read back the updated value
        cursor = await db.execute(
            "SELECT api_calls FROM api_usage WHERE month = ?", (month,)
        )
        row = await cursor.fetchone()
        new_count = row["api_calls"] if row else 1
        logger.info(f"[Budget] API call recorded. Total this month: {new_count}/{MONTHLY_API_LIMIT}")
        return new_count
    finally:
        await db.close()


async def get_usage_stats() -> dict:
    """
    Returns full usage statistics for the admin /api/system/api-usage endpoint.
    """
    usage = await get_monthly_usage()
    return {
        "monthly_limit": MONTHLY_API_LIMIT,
        "calls_used": usage["api_calls"],
        "calls_remaining": usage["calls_remaining"],
        "month": usage["month"],
        "last_call_at": usage["last_call_at"],
        "budget_breakdown": {
            "catalog": CATALOG_BUDGET,
            "search": SEARCH_BUDGET,
            "trending": TRENDING_BUDGET,
            "emergency": EMERGENCY_BUDGET,
        },
    }
