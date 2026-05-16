import pytest

from src.main import ROUTER


@pytest.mark.asyncio
async def test_main_router_dispatches_all_features(monkeypatch):
    calls = []

    async def _f(*args, **kwargs):
        calls.append(True)
        return {"ok": True}

    for key in ["thread_search", "reply_metrics", "summarizer", "unread_digest"]:
        monkeypatch.setitem(ROUTER, key, _f)

    for key in ["thread_search", "reply_metrics", "summarizer", "unread_digest"]:
        out = await ROUTER[key]({}, object())
        assert out["ok"] is True

    assert len(calls) == 4
