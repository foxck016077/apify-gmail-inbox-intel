import pytest

from src import reply_metrics


class _Req:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return self._data


class _Threads:
    def list(self, **kwargs):
        return _Req({"threads": [{"id": "t1"}]})

    def get(self, userId, id, format):
        return _Req(
            {
                "id": "t1",
                "messages": [
                    {
                        "id": "m1",
                        "internalDate": "1600000000000",
                        "payload": {"headers": [{"name": "From", "value": "A <a@foo.com>"}]},
                    },
                    {
                        "id": "m2",
                        "internalDate": "1600003600000",
                        "payload": {"headers": []},
                    },
                ],
            }
        )


class _Users:
    def __init__(self):
        self._threads = _Threads()

    def threads(self):
        return self._threads


class _Svc:
    def users(self):
        return _Users()


@pytest.mark.asyncio
async def test_reply_metrics_over_sla(monkeypatch):
    async def fake_quota(user_id, count, now=None):
        return {"used": count}

    monkeypatch.setattr(reply_metrics, "enforce_and_consume_quota", fake_quota)
    out = await reply_metrics.run_reply_metrics(
        {"from_domains": ["foo.com"], "sla_days": 1, "max_results": 10},
        _Svc(),
    )
    assert out["summary"]["total"] == 1
    assert out["summary"]["over_sla_count"] == 1
    assert out["threads_over_sla"][0]["reply_chain_length"] == 2
    # default include_reengage_angles=false → no suggested_angles key
    assert "suggested_angles" not in out["threads_over_sla"][0]


@pytest.mark.asyncio
async def test_reply_metrics_with_reengage_angles(monkeypatch):
    async def fake_quota(user_id, count, now=None):
        return {"used": count}

    monkeypatch.setattr(reply_metrics, "enforce_and_consume_quota", fake_quota)
    monkeypatch.setattr(
        reply_metrics,
        "_fetch_news_rss",
        lambda company, lookback, max_items: [
            {"headline": f"{company} ships new product", "url": "https://example.com", "pub_date": "Mon", "source": "TechCrunch"}
        ],
    )
    out = await reply_metrics.run_reply_metrics(
        {"from_domains": ["foo.com"], "sla_days": 1, "max_results": 10, "include_reengage_angles": True},
        _Svc(),
    )
    assert out["threads_over_sla"][0]["suggested_angles"]
    assert "foo" in out["threads_over_sla"][0]["suggested_angles"][0]["headline"]
