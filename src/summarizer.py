from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

try:
    from openai import AsyncOpenAI
except ImportError:  # pragma: no cover
    class AsyncOpenAI:  # type: ignore[override]
        def __init__(self, *args, **kwargs):
            raise RuntimeError("openai package is required for summarizer")

from .quota import enforce_and_consume_quota


def _execute(req):
    return req.execute()


def _extract_body(msg: Dict[str, Any]) -> str:
    payload = msg.get("payload", {})
    parts = payload.get("parts") or []
    for part in parts:
        body = part.get("body", {}).get("data")
        if body:
            return body[:4000]
    return (payload.get("body", {}).get("data") or "")[:4000]


async def run_summarizer(input_data: Dict[str, Any], gmail_service) -> Dict[str, Any]:
    api_key = (input_data.get("openai_api_key") or "").strip()
    if not api_key:
        return {"summaries": [], "status": "skipped", "reason": "openai_api_key missing"}

    query = input_data.get("query") or "in:inbox"
    max_results = int(input_data.get("max_results") or 20)
    model = input_data.get("summary_model") or "gpt-4o-mini"

    list_resp = _execute(gmail_service.users().threads().list(userId="me", q=query, maxResults=max_results))
    refs = list_resp.get("threads", [])

    quota = await enforce_and_consume_quota(input_data.get("free_tier_user_id"), len(refs))

    client = AsyncOpenAI(api_key=api_key)
    summaries: List[Dict[str, Any]] = []

    for ref in refs:
        thread = _execute(gmail_service.users().threads().get(userId="me", id=ref["id"], format="metadata"))
        messages = thread.get("messages") or []
        bodies: List[str] = []
        for m in messages[:5]:
            msg_full = _execute(
                gmail_service.users().messages().get(userId="me", id=m["id"], format="full")
            )
            bodies.append(_extract_body(msg_full))

        excerpt = "\n---\n".join(bodies)
        prompt = (
            "Summarize this Gmail thread and return JSON with keys "
            "gist, action_items(list), sentiment(one of positive/neutral/negative).\n\n"
            f"Thread excerpt:\n{excerpt}"
        )

        completion = await client.responses.create(
            model=model,
            input=prompt,
            temperature=0.2,
        )
        text = completion.output_text or ""
        usage = getattr(completion, "usage", None)
        in_tok = getattr(usage, "input_tokens", 0) if usage else 0
        out_tok = getattr(usage, "output_tokens", 0) if usage else 0
        cost = round((in_tok * 0.00000015) + (out_tok * 0.0000006), 6)

        summaries.append(
            {
                "thread_id": thread.get("id"),
                "gist": text[:400],
                "action_items": [],
                "sentiment": "neutral",
                "cost_usd": cost,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        )

    return {"summaries": summaries, "quota": quota}
