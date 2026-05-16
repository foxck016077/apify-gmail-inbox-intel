from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from email.utils import parseaddr
from typing import Any, Dict, List

from .quota import enforce_and_consume_quota


def _execute(req):
    return req.execute()


def _sender_domain(message: Dict[str, Any]) -> str:
    headers = message.get("payload", {}).get("headers", [])
    from_value = ""
    for h in headers:
        if (h.get("name") or "").lower() == "from":
            from_value = h.get("value") or ""
    _, addr = parseaddr(from_value)
    return addr.split("@")[-1].lower() if "@" in addr else "unknown"


async def run_unread_digest(input_data: Dict[str, Any], gmail_service) -> Dict[str, Any]:
    after_days = int(input_data.get("afterDays") or input_data.get("after_days") or 7)
    query = f"is:unread in:inbox newer_than:{after_days}d"
    max_results = int(input_data.get("max_results") or 100)

    resp = _execute(gmail_service.users().threads().list(userId="me", q=query, maxResults=max_results))
    refs = resp.get("threads", [])

    threads: List[Dict[str, Any]] = []
    domain_counter: Counter[str] = Counter()
    label_counter: Counter[str] = Counter()

    oldest = None

    for ref in refs:
        thread = _execute(gmail_service.users().threads().get(userId="me", id=ref["id"], format="metadata"))
        messages = thread.get("messages") or []
        if not messages:
            continue
        first = messages[0]
        domain = _sender_domain(first)
        labels = first.get("labelIds") or []

        domain_counter[domain] += 1
        for lab in labels:
            label_counter[lab] += 1

        ts = int(first.get("internalDate") or 0)
        if oldest is None or ts < oldest["internalDateMs"]:
            oldest = {
                "thread_id": thread.get("id"),
                "internalDateMs": ts,
                "iso": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(),
                "domain": domain,
            }

        threads.append({"thread_id": thread.get("id"), "domain": domain, "labels": labels, "internalDate": ts})

    quota = await enforce_and_consume_quota(input_data.get("free_tier_user_id"), len(threads))

    md_lines = [
        "# Unread Inbox Digest",
        "",
        f"- 未讀總數: **{len(threads)}**",
        "",
        "## 按 domain 分組 top 10",
    ]
    for domain, count in domain_counter.most_common(10):
        md_lines.append(f"- {domain}: {count}")

    md_lines.extend(["", "## 按 label 分組 top 5"])
    for label, count in label_counter.most_common(5):
        md_lines.append(f"- {label}: {count}")

    md_lines.extend(["", "## 最舊未讀（風險）"])
    if oldest:
        md_lines.append(f"- thread_id: {oldest['thread_id']} | {oldest['iso']} | domain={oldest['domain']}")
    else:
        md_lines.append("- 無")

    markdown = "\n".join(md_lines)
    return {
        "query": query,
        "total_unread": len(threads),
        "by_domain": dict(domain_counter.most_common(10)),
        "by_label": dict(label_counter.most_common(5)),
        "oldest_unread": oldest,
        "markdown": markdown,
        "quota": quota,
    }
