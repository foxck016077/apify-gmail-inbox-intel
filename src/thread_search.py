from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from .quota import enforce_and_consume_quota


def _execute(req):
    return req.execute()


def _parse_message_headers(message: Dict[str, Any]) -> Dict[str, str]:
    headers = message.get("payload", {}).get("headers", [])
    out = {"from": "", "to": "", "subject": ""}
    for item in headers:
        name = (item.get("name") or "").lower()
        if name in out:
            out[name] = item.get("value") or ""
    return out


def _map_thread(thread: Dict[str, Any]) -> Dict[str, Any]:
    first_message = (thread.get("messages") or [{}])[0]
    headers = _parse_message_headers(first_message)
    return {
        "id": thread.get("id"),
        "snippet": thread.get("snippet", ""),
        "from": headers["from"],
        "to": headers["to"],
        "subject": headers["subject"],
        "internalDate": first_message.get("internalDate"),
        "messages_count": len(thread.get("messages") or []),
    }


def _normalize_api_error(exc: Exception) -> RuntimeError:
    msg = str(exc)
    if "403" in msg or "quota" in msg.lower() or "rate" in msg.lower():
        return RuntimeError(f"Gmail API quota/permission error: {msg}")
    if "50" in msg or "backendError" in msg:
        return RuntimeError(f"Gmail API server error (5xx): {msg}")
    return RuntimeError(f"Gmail API error: {msg}")


async def run_thread_search(input_data: Dict[str, Any], gmail_service) -> Dict[str, Any]:
    query = input_data.get("query") or "in:inbox"
    max_results = int(input_data.get("max_results") or 50)

    try:
        list_resp = _execute(
            gmail_service.users().threads().list(userId="me", q=query, maxResults=max_results)
        )
        thread_refs = list_resp.get("threads", [])

        mapped: List[Dict[str, Any]] = []
        for item in thread_refs:
            thread = _execute(
                gmail_service.users()
                .threads()
                .get(userId="me", id=item["id"], format="metadata")
            )
            mapped.append(_map_thread(thread))

        quota = await enforce_and_consume_quota(
            input_data.get("free_tier_user_id"),
            len(mapped),
        )

        return {
            "threads": mapped,
            "total": len(mapped),
            "query": query,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "quota": quota,
        }
    except Exception as exc:  # pragma: no cover
        raise _normalize_api_error(exc) from exc
