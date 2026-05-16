from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from apify import Actor
except ImportError:  # pragma: no cover
    class Actor:  # type: ignore[override]
        @staticmethod
        async def open_key_value_store():
            raise RuntimeError("apify package is required at runtime")

FREE_TIER_LIMIT = 100


class QuotaExceededError(RuntimeError):
    """Raised when the free monthly quota is exceeded."""


@dataclass
class QuotaState:
    key: str
    used: int
    limit: int


def _month_key(free_tier_user_id: str, now: Optional[datetime] = None) -> str:
    ts = now or datetime.now(timezone.utc)
    return f"free_quota_{free_tier_user_id}_{ts.strftime('%Y-%m')}"


async def enforce_and_consume_quota(
    free_tier_user_id: Optional[str],
    threads_inspected: int,
    *,
    now: Optional[datetime] = None,
) -> Optional[Dict[str, Any]]:
    """Track free-tier monthly usage in KV store and fail on overflow.

    Returns None when no free-tier user id is provided (quota tracking disabled).
    """
    if not free_tier_user_id:
        return None

    increment = max(int(threads_inspected or 0), 0)
    store = await Actor.open_key_value_store()
    key = _month_key(free_tier_user_id, now=now)

    payload = await store.get_value(key) or {}
    used_before = int(payload.get("used", 0))
    used_after = used_before + increment

    if used_after > FREE_TIER_LIMIT:
        raise QuotaExceededError(
            (
                f"Free tier quota exceeded: {used_after}/{FREE_TIER_LIMIT} threads this month. "
                "Please upgrade to Pro or add pay-per-result budget."
            )
        )

    await store.set_value(
        key,
        {
            "used": used_after,
            "limit": FREE_TIER_LIMIT,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    return {"key": key, "used": used_after, "limit": FREE_TIER_LIMIT}
