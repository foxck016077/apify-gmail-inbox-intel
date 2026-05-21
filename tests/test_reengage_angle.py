from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from unittest.mock import patch

import pytest

from src.reengage_angle import (
    _company_slug_from_domain,
    _extract_domain,
    run_reengage_angle,
)


def test_company_slug_from_corporate_domain():
    assert _company_slug_from_domain("stripe.com") == "stripe"
    assert _company_slug_from_domain("acme-corp.co.uk") == "acme corp"
    assert _company_slug_from_domain("mail.notion.so") == "notion"


def test_company_slug_skips_generic_consumer_domains():
    assert _company_slug_from_domain("gmail.com") == ""
    assert _company_slug_from_domain("yahoo.com") == ""
    assert _company_slug_from_domain("protonmail.com") == ""
    assert _company_slug_from_domain("") == ""


def test_extract_domain_basic():
    assert _extract_domain("Alex <alex@stripe.com>") == "stripe.com"
    assert _extract_domain("no-name@acme.co") == "acme.co"
    assert _extract_domain("") == ""


def _make_thread(thread_id: str, from_addr: str, days_silent: float, subject: str = "Re: project") -> dict:
    last_dt = datetime.now(timezone.utc) - timedelta(days=days_silent)
    return {
        "id": thread_id,
        "messages": [
            {
                "internalDate": str(int((last_dt - timedelta(days=days_silent + 1)).timestamp() * 1000)),
                "payload": {"headers": [{"name": "From", "value": from_addr}, {"name": "Subject", "value": subject}]},
            },
            {"internalDate": str(int(last_dt.timestamp() * 1000)), "payload": {"headers": []}},
        ],
    }


class FakeReq:
    def __init__(self, payload):
        self._payload = payload

    def execute(self):
        return self._payload


class FakeUsers:
    def __init__(self, threads_obj):
        self._threads = threads_obj

    def threads(self):
        return self._threads


class FakeThreadsAPI:
    def __init__(self, list_payload, threads_by_id):
        self._list_payload = list_payload
        self._threads_by_id = threads_by_id

    def list(self, userId, q, maxResults):  # noqa: N803
        return FakeReq(self._list_payload)

    def get(self, userId, id, format):  # noqa: N803, A002
        return FakeReq(self._threads_by_id[id])


class FakeService:
    def __init__(self, list_payload, threads_by_id):
        self._users = FakeUsers(FakeThreadsAPI(list_payload, threads_by_id))

    def users(self):
        return self._users


def test_run_reengage_angle_filters_under_sla_and_generic_domains():
    threads_by_id = {
        "t_cold": _make_thread("t_cold", "Alex <alex@stripe.com>", 30, "Re: payments rollout"),
        "t_warm": _make_thread("t_warm", "Bob <bob@notion.so>", 3, "Re: doc draft"),
        "t_generic": _make_thread("t_generic", "Carol <carol@gmail.com>", 30, "Re: catch up"),
        "t_dormant": _make_thread("t_dormant", "Dave <dave@acme.io>", 180, "Re: Q3 brand refresh"),
    }
    list_payload = {"threads": [{"id": "t_cold"}, {"id": "t_warm"}, {"id": "t_generic"}, {"id": "t_dormant"}]}
    svc = FakeService(list_payload, threads_by_id)

    with patch("src.reengage_angle._fetch_news_rss", return_value=[{"headline": "Stripe ships new tool", "url": "https://example.com/s", "pub_date": "X", "source": "Y"}]):
        with patch("src.reengage_angle.enforce_and_consume_quota", new=_fake_quota):
            result = asyncio.run(run_reengage_angle({"sla_days": 14, "dormant_days": 90}, svc))

    assert result["summary"]["total_cold_threads"] == 2
    assert result["summary"]["skipped_generic_domain"] == 1
    assert result["summary"]["cold_tier_count"] == 1
    assert result["summary"]["dormant_tier_count"] == 1

    by_id = {t["thread_id"]: t for t in result["cold_threads_with_re_engage_angles"]}
    assert by_id["t_cold"]["tier"] == "cold"
    assert by_id["t_dormant"]["tier"] == "dormant"
    assert by_id["t_cold"]["draft_emails"] == []
    assert "tier_guide" in result


def test_run_reengage_angle_skips_llm_when_no_api_key():
    """Confirm LLM enrichment is gated by openai_api_key (no key = no LLM call)."""
    threads_by_id = {"t_cold": _make_thread("t_cold", "Alex <alex@stripe.com>", 30)}
    svc = FakeService({"threads": [{"id": "t_cold"}]}, threads_by_id)

    with patch("src.reengage_angle._fetch_news_rss", return_value=[{"headline": "h", "url": "u", "pub_date": "p", "source": "s"}]):
        with patch("src.reengage_angle.enforce_and_consume_quota", new=_fake_quota):
            # openai_api_key omitted → no LLM call
            result = asyncio.run(run_reengage_angle({"sla_days": 14}, svc))
    assert result["cold_threads_with_re_engage_angles"][0]["draft_emails"] == []


async def _fake_quota(uid, count):
    return {"allowed": True, "consumed": count}


def test_news_rss_parsing_strips_source_suffix():
    """Google News titles often end with ' - Source Name'; strip it from headline."""
    from src.reengage_angle import _fetch_news_rss
    from unittest.mock import patch
    fake_rss = """<rss><channel>
        <item>
            <title>Stripe ships new tool - TechCrunch</title>
            <link>https://example.com/a</link>
            <pubDate>Mon, 20 May 2026 10:00:00 GMT</pubDate>
            <source url="https://techcrunch.com">TechCrunch</source>
        </item>
        <item>
            <title><![CDATA[Acme closes Series B - Business Wire]]></title>
            <link>https://example.com/b</link>
            <pubDate>Tue, 21 May 2026 12:00:00 GMT</pubDate>
            <source url="https://businesswire.com">Business Wire</source>
        </item>
    </channel></rss>"""

    class _FakeResp:
        def read(self):
            return fake_rss.encode()

    with patch("src.reengage_angle.urllib.request.urlopen", return_value=_FakeResp()):
        items = _fetch_news_rss("stripe", 90, 5)

    assert len(items) == 2
    assert items[0]["headline"] == "Stripe ships new tool"  # source suffix stripped
    assert items[0]["source"] == "TechCrunch"
    assert items[1]["headline"] == "Acme closes Series B"  # CDATA + suffix both handled
    assert items[1]["source"] == "Business Wire"


def test_news_rss_filters_empty_headlines():
    """Items without a parseable headline should be dropped."""
    from src.reengage_angle import _fetch_news_rss
    from unittest.mock import patch
    fake_rss = """<rss><channel>
        <item><title></title><link>x</link></item>
        <item><title>Real headline</title><link>y</link></item>
    </channel></rss>"""

    class _FakeResp:
        def read(self):
            return fake_rss.encode()

    with patch("src.reengage_angle.urllib.request.urlopen", return_value=_FakeResp()):
        items = _fetch_news_rss("acme", 90, 5)
    assert len(items) == 1
    assert items[0]["headline"] == "Real headline"


def test_news_rss_respects_max_items_cap():
    """RSS response with more items than max_items should be sliced before parsing."""
    from src.reengage_angle import _fetch_news_rss
    from unittest.mock import patch

    item_block = "".join(
        f"<item><title>Headline {i}</title><link>https://example.com/{i}</link>"
        f"<pubDate>Mon, 20 May 2026 10:00:00 GMT</pubDate></item>"
        for i in range(10)
    )
    fake_rss = f"<rss><channel>{item_block}</channel></rss>"

    class _FakeResp:
        def read(self):
            return fake_rss.encode()

    with patch("src.reengage_angle.urllib.request.urlopen", return_value=_FakeResp()):
        items = _fetch_news_rss("acme", 90, 3)
    assert len(items) == 3
    assert items[0]["headline"] == "Headline 0"
    assert items[2]["headline"] == "Headline 2"
