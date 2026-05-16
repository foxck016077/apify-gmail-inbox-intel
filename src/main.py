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

        if input_data.get("dry_run", False):
            result = {"status": "ok", "feature": feature, "dry_run": True}
        else:
            result = await ROUTER[feature](input_data, gmail_service)

        await Actor.push_data(result)

    clear_token_state(creds)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
