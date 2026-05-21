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
    }
    list_payload = {"threads": [{"id": "t_cold"}, {"id": "t_warm"}, {"id": "t_generic"}]}
    svc = FakeService(list_payload, threads_by_id)

    with patch("src.reengage_angle._fetch_news_rss", return_value=[{"headline": "Stripe ships new tool", "url": "https://example.com/s", "pub_date": "X", "source": "Y"}]):
        with patch("src.reengage_angle.enforce_and_consume_quota", new=_fake_quota):
            result = asyncio.run(run_reengage_angle({"sla_days": 14}, svc))

    assert result["summary"]["total_cold_threads"] == 1
    assert result["summary"]["skipped_generic_domain"] == 1
    cold = result["cold_threads_with_re_engage_angles"][0]
    assert cold["company_search_term"] == "stripe"
    assert len(cold["suggested_angles"]) == 1
    assert cold["draft_emails"] == []  # no openai_api_key → empty


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
