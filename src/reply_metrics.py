from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parseaddr
from statistics import mean
from typing import Any, Dict, List

from .quota import enforce_and_consume_quota
from .reengage_angle import _company_slug_from_domain, _fetch_news_rss


def _execute(req):
    return req.execute()


def _extract_domain(sender: str) -> str:
    _, addr = parseaddr(sender or "")
    return addr.split("@")[-1].lower() if "@" in addr else ""


def _dt_from_ms(ms: str | None) -> datetime:
    v = int(ms or 0) / 1000
    return datetime.fromtimestamp(v, tz=timezone.utc)


def _priority_band(days_since: float, sla_days: int) -> str:
    if sla_days <= 0:
        return "COLD"
    ratio = days_since / sla_days
    if ratio < 1.5:
        return "HOT"
    if ratio < 3:
        return "WARM"
    return "COLD"


def _thread_sender_domain(thread: Dict[str, Any]) -> str:
    first = (thread.get("messages") or [{}])[0]
    headers = first.get("payload", {}).get("headers", [])
    sender = ""
    for h in headers:
        if (h.get("name") or "").lower() == "from":
            sender = h.get("value") or ""
            break
    return _extract_domain(sender)


async def run_reply_metrics(input_data: Dict[str, Any], gmail_service) -> Dict[str, Any]:
    query = input_data.get("query") or "in:inbox"
    max_results = int(input_data.get("max_results") or 50)
    domains = {d.lower() for d in (input_data.get("from_domains") or []) if d}
    sla_days = int(input_data.get("sla_days") or 7)
    include_reengage_angles = bool(input_data.get("include_reengage_angles", False))
    news_lookback_days = int(input_data.get("news_lookback_days") or 90)
    max_news_per_thread = int(input_data.get("max_news_per_thread") or 5)

    list_resp = _execute(
        gmail_service.users().threads().list(userId="me", q=query, maxResults=max_results)
    )
    refs = list_resp.get("threads", [])

    now = datetime.now(timezone.utc)
    over_sla: List[Dict[str, Any]] = []
    responded: List[Dict[str, Any]] = []
    response_hours: List[float] = []

    for ref in refs:
        thread = _execute(gmail_service.users().threads().get(userId="me", id=ref["id"], format="metadata"))
        domain = _thread_sender_domain(thread)
        if domains and domain not in domains:
            continue

        messages = thread.get("messages") or []
        if not messages:
            continue
        last_dt = _dt_from_ms(messages[-1].get("internalDate"))
        days_since = (now - last_dt).total_seconds() / 86400
        over = days_since > sla_days
        item = {
            "thread_id": thread.get("id"),
            "last_message_at": last_dt.isoformat(),
            "days_since_last_reply": round(days_since, 2),
            "over_sla": over,
            "reply_chain_length": len(messages),
            "sender_domain": domain,
        }
        if over:
            item["priority_band"] = _priority_band(days_since, sla_days)

        if len(messages) >= 2:
            first_dt = _dt_from_ms(messages[0].get("internalDate"))
            response_hours.append((last_dt - first_dt).total_seconds() / 3600)

        if item["over_sla"]:
            if include_reengage_angles:
                company = _company_slug_from_domain(domain)
                if company:
                    item["suggested_angles"] = _fetch_news_rss(
                        company, news_lookback_days, max_news_per_thread
                    )
                else:
                    item["suggested_angles"] = []
            over_sla.append(item)
        else:
            responded.append(item)

    quota = await enforce_and_consume_quota(input_data.get("free_tier_user_id"), len(over_sla) + len(responded))

    priority_breakdown = {"HOT": 0, "WARM": 0, "COLD": 0}
    for t in over_sla:
        band = t.get("priority_band")
        if band in priority_breakdown:
            priority_breakdown[band] += 1

    return {
        "threads_over_sla": over_sla,
        "threads_responded": responded,
        "summary": {
            "total": len(over_sla) + len(responded),
            "over_sla_count": len(over_sla),
            "priority_breakdown": priority_breakdown,
            "avg_response_hours": round(mean(response_hours), 2) if response_hours else 0,
        },
        "quota": quota,
    }
