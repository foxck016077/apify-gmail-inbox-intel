"""Gmail API client utilities for Apify Actor runtime.

Phase 2.1 skeleton:
- Accept OAuth refresh credentials from Actor input
- Exchange refresh_token -> short-lived access token in memory
- Build Gmail API service client
- Provide safe logging helpers (mask email/token)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
except ImportError:  # pragma: no cover
    Request = None  # type: ignore[assignment]
    Credentials = None  # type: ignore[assignment]

    def build(*args, **kwargs):  # type: ignore[override]
        raise RuntimeError("google-api-python-client and google-auth are required")

GMAIL_READONLY_SCOPE = "https://www.googleapis.com/auth/gmail.readonly"
TOKEN_URI = "https://oauth2.googleapis.com/token"


@dataclass
class GmailOAuthInput:
    refresh_token: str
    client_id: str
    client_secret: str


def mask_secret(value: Optional[str]) -> str:
    if not value:
        return "<empty>"
    tail = value[-4:] if len(value) >= 4 else value
    return f"***{tail}"


def mask_email(email: Optional[str]) -> str:
    if not email:
        return "<empty>"
    local, _, domain = email.partition("@")
    local_masked = f"***{local[-1:]}" if local else "***"
    domain_tail = domain[-4:] if domain else ""
    return f"{local_masked}@***{domain_tail}"


def build_credentials(oauth: GmailOAuthInput) -> Credentials:
    """Create credentials object and refresh access token in memory only."""
    if Credentials is None or Request is None:
        raise RuntimeError("google-auth dependencies are required")

    creds = Credentials(
        token=None,
        refresh_token=oauth.refresh_token,
        token_uri=TOKEN_URI,
        client_id=oauth.client_id,
        client_secret=oauth.client_secret,
        scopes=[GMAIL_READONLY_SCOPE],
    )
    creds.refresh(Request())
    return creds


def build_gmail_service(oauth: GmailOAuthInput):
    """Build Gmail v1 client using refreshed credentials."""
    creds = build_credentials(oauth)
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    return service, creds


def clear_token_state(creds: Optional[Credentials]) -> None:
    """Best-effort cleanup of in-memory token fields after run."""
    if not creds:
        return
    creds.token = None
    creds.refresh_token = None
    creds.id_token = None


def get_profile(service) -> Dict[str, Any]:
    return service.users().getProfile(userId="me").execute()
