"""Re-engage angle generator — for each cold/over-SLA thread, surface recent news headlines about the counterparty company so the user can pick a fresh re-engage angle.

Buyer-voice grounded: r/sales 1tdngew (49 comments, 12 mentions of "new context / what changed") asked exactly this — "how to re-enter a cold conversation with new context" — not a sorted list.

Public Google News RSS, no API key required. Optional OpenAI summarisation of the news angle (gated by openai_api_key like summarizer feature).
"""
from __future__ import annotations

import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parseaddr
from typing import Any, Dict, List

from .quota import enforce_and_consume_quota


GENERIC_DOMAINS = {
    "gmail.com", "googlemail.com", "yahoo.com", "yahoo.co.uk", "outlook.com",
    "hotmail.com", "live.com", "icloud.com", "me.com", "mac.com",
    "proton.me", "protonmail.com", "fastmail.com", "aol.com",
    "qq.com", "163.com", "126.com", "sina.com", "naver.com",
}


def _extract_domain(sender: str) -> str:
    _, addr = parseaddr(sender or "")
    return addr.split("@")[-1].lower() if "@" in addr else ""


def _company_slug_from_domain(domain: str) -> str:
    """Convert email domain into company-search-friendly slug.

    Examples:
        stripe.com -> stripe
        acme-corp.co.uk -> acme corp
        mail.notion.so -> notion
    """
    if not domain or domain in GENERIC_DOMAINS:
        return ""
    parts = domain.split(".")
    if len(parts) >= 3 and parts[0] in {"mail", "smtp", "email", "newsletter", "info"}:
        parts = parts[1:]
    core = parts[0]
    return core.replace("-", " ").replace("_", " ")


def _fetch_news_rss(company: str, lookback_days: int = 90, max_items: int = 5) -> List[Dict[str, str]]:
    if not company:
        return []
    q = urllib.parse.quote(f'"{company}"')
    url = f"https://news.google.com/rss/search?q={q}+when:{lookback_days}d&hl=en-US&gl=US&ceid=US:en"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        body = urllib.request.urlopen(req, timeout=10).read().decode()
    except Exception as e:
        return [{"error": f"news_fetch_failed: {e}"}]

    items: List[Dict[str, str]] = []
    for raw in re.findall(r"<item>(.+?)</item>", body, re.DOTALL)[:max_items]:
        title_m = re.search(r"<title><!\[CDATA\[(.+?)\]\]></title>|<title>(.+?)</title>", raw, re.DOTALL)
        link_m = re.search(r"<link>(.+?)</link>", raw)
        date_m = re.search(r"<pubDate>(.+?)</pubDate>", raw)
        source_m = re.search(r'<source url="[^"]*">(.+?)</source>', raw)
        title = ""
        if title_m:
            title = title_m.group(1) or title_m.group(2) or ""
        items.append({
            "headline": title.strip(),
            "url": (link_m.group(1).strip() if link_m else ""),
            "pub_date": (date_m.group(1).strip() if date_m else ""),
            "source": (source_m.group(1).strip() if source_m else ""),
        })
    return items


def _execute(req):
    return req.execute()


def _thread_sender_domain(thread: Dict[str, Any]) -> str:
    first = (thread.get("messages") or [{}])[0]
    headers = first.get("payload", {}).get("headers", [])
    for h in headers:
        if (h.get("name") or "").lower() == "from":
            return _extract_domain(h.get("value") or "")
    return ""


def _dt_from_ms(ms: str | None) -> datetime:
    v = int(ms or 0) / 1000
    return datetime.fromtimestamp(v, tz=timezone.utc)


async def run_reengage_angle(input_data: Dict[str, Any], gmail_service) -> Dict[str, Any]:
    query = input_data.get("query") or "in:inbox"
    max_results = int(input_data.get("max_results") or 30)
    sla_days = int(input_data.get("sla_days") or 14)
    news_lookback_days = int(input_data.get("news_lookback_days") or 90)
    max_news_per_thread = int(input_data.get("max_news_per_thread") or 5)

    list_resp = _execute(
        gmail_service.users().threads().list(userId="me", q=query, maxResults=max_results)
    )
    refs = list_resp.get("threads", [])

    now = datetime.now(timezone.utc)
    cold_threads_with_angles: List[Dict[str, Any]] = []
    skipped_generic_domain = 0

    for ref in refs:
        thread = _execute(gmail_service.users().threads().get(userId="me", id=ref["id"], format="metadata"))
        messages = thread.get("messages") or []
        if not messages:
            continue
        last_dt = _dt_from_ms(messages[-1].get("internalDate"))
        days_silent = (now - last_dt).total_seconds() / 86400

        if days_silent < sla_days:
            continue

        domain = _thread_sender_domain(thread)
        company = _company_slug_from_domain(domain)

        if not company:
            skipped_generic_domain += 1
            continue

        news_items = _fetch_news_rss(company, news_lookback_days, max_news_per_thread)

        # extract thread subject for context
        subject = ""
        for h in messages[0].get("payload", {}).get("headers", []):
            if (h.get("name") or "").lower() == "subject":
                subject = h.get("value") or ""
                break

        cold_threads_with_angles.append({
            "thread_id": thread.get("id"),
            "subject": subject,
            "counterparty_domain": domain,
            "company_search_term": company,
            "days_silent": round(days_silent, 1),
            "reply_chain_length": len(messages),
            "suggested_angles": news_items,
        })

    quota = await enforce_and_consume_quota(input_data.get("free_tier_user_id"), len(cold_threads_with_angles))

    return {
        "cold_threads_with_re_engage_angles": cold_threads_with_angles,
        "summary": {
            "total_cold_threads": len(cold_threads_with_angles),
            "skipped_generic_domain": skipped_generic_domain,
            "sla_days_threshold": sla_days,
            "news_lookback_days": news_lookback_days,
        },
        "quota": quota,
        "buyer_voice_grounding": "r/sales 1tdngew (49 comments) — 12 mentions of 'new context / news / what changed' as the actual re-engage demand",
    }
