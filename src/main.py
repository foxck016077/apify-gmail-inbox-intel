"""Apify Actor entrypoint for Gmail Inbox Intelligence (Phase 2.1 skeleton)."""

from __future__ import annotations

from typing import Any, Dict

try:
    from apify import Actor
except ImportError:  # pragma: no cover
    class Actor:  # type: ignore[override]
        log = type("_L", (), {"info": staticmethod(lambda *args, **kwargs: None)})()

        @staticmethod
        async def get_input():
            return {}

        @staticmethod
        async def push_data(_):
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return None

from .gmail_client import (
    GmailOAuthInput,
    build_gmail_service,
    clear_token_state,
    get_profile,
    mask_email,
    mask_secret,
)
from .digest import run_unread_digest
from .reply_metrics import run_reply_metrics
from .summarizer import run_summarizer
from .thread_search import run_thread_search


ROUTER = {
    "thread_search": run_thread_search,
    "reply_metrics": run_reply_metrics,
    "summarizer": run_summarizer,
    "unread_digest": run_unread_digest,
}


async def main() -> None:
    creds = None
    async with Actor:
        input_data = await Actor.get_input() or {}

        feature = input_data.get("feature", "thread_search")
        oauth_token = input_data.get("oauth_token") or {}

        if feature not in ROUTER:
            raise ValueError(f"Unsupported feature: {feature}")

        if input_data.get("dry_run", False):
            Actor.log.info("dry_run=true — skipping OAuth + Gmail API, emitting synthetic sample")
            for item in _dry_run_sample(feature, input_data):
                await Actor.push_data(item)
            return

        oauth = GmailOAuthInput(
            refresh_token=oauth_token.get("refresh_token", ""),
            client_id=oauth_token.get("client_id", ""),
            client_secret=oauth_token.get("client_secret", ""),
        )

        if not (oauth.refresh_token and oauth.client_id and oauth.client_secret):
            raise ValueError("oauth_token.refresh_token/client_id/client_secret are required")

        Actor.log.info(
            "Starting feature=%s oauth(refresh=%s client_id=%s secret=%s)",
            feature,
            mask_secret(oauth.refresh_token),
            mask_secret(oauth.client_id),
            mask_secret(oauth.client_secret),
        )

        gmail_service, creds = build_gmail_service(oauth)
        profile = get_profile(gmail_service)
        Actor.log.info("Authenticated as %s", mask_email(profile.get("emailAddress")))

        result = await ROUTER[feature](input_data, gmail_service)
        await Actor.push_data(result)

    clear_token_state(creds)


def _dry_run_sample(feature: str, input_data: Dict[str, Any]) -> list:
    """Synthetic dataset for Apify Store sample runs (no real Gmail call)."""
    query = input_data.get("query", "in:inbox newer_than:7d")
    if feature == "thread_search":
        return [
            {"thread_id": "demo_t1", "subject": "Re: Q3 proposal — timeline check", "message_count": 4, "last_message_at": "2026-05-15T09:12:00Z", "query": query, "dry_run": True},
            {"thread_id": "demo_t2", "subject": "Project kickoff: Acme migration", "message_count": 2, "last_message_at": "2026-05-13T14:30:00Z", "query": query, "dry_run": True},
            {"thread_id": "demo_t3", "subject": "Invoice INV-2026-041 — paid", "message_count": 1, "last_message_at": "2026-05-12T08:00:00Z", "query": query, "dry_run": True},
        ]
    if feature == "reply_metrics":
        return [
            {"thread_id": "demo_t1", "subject": "Re: Q3 proposal — timeline check", "reply_from_me": 2, "reply_from_others": 2, "last_reply_age_days": 2, "sla_breach": False, "dry_run": True},
            {"thread_id": "demo_t4", "subject": "Onboarding docs — pending", "reply_from_me": 3, "reply_from_others": 0, "last_reply_age_days": 9, "sla_breach": True, "sla_threshold_days": 7, "dry_run": True},
            {"thread_id": "demo_t5", "subject": "Re: Contract terms", "reply_from_me": 1, "reply_from_others": 0, "last_reply_age_days": 18, "sla_breach": True, "sla_threshold_days": 7, "dry_run": True},
        ]
    if feature == "summarizer":
        return [
            {"thread_id": "demo_t1", "subject": "Re: Q3 proposal — timeline check", "summary": "Client asked for 2-week timeline shift on Q3 deliverable. You confirmed. Awaiting their signed amendment.", "tokens_used": 142, "dry_run": True},
        ]
    if feature == "unread_digest":
        return [
            {"label": "Clients/Acme", "unread_count": 3, "thread_ids": ["demo_t1", "demo_t4", "demo_t7"], "window_hours": 24, "dry_run": True},
            {"label": "Sales/Inbound", "unread_count": 5, "thread_ids": ["demo_t2", "demo_t8", "demo_t9", "demo_t10", "demo_t11"], "window_hours": 24, "dry_run": True},
            {"label": "Personal", "unread_count": 1, "thread_ids": ["demo_t6"], "window_hours": 24, "dry_run": True},
        ]
    return [{"feature": feature, "dry_run": True, "status": "ok"}]


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
