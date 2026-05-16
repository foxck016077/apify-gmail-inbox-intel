import pytest

from src import digest


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
                        "internalDate": "1700000000000",
                        "labelIds": ["INBOX", "CATEGORY_UPDATES"],
                        "payload": {"headers": [{"name": "From", "value": "A <a@foo.com>"}]},
                    }
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
async def test_digest_markdown_structure(monkeypatch):
    async def fake_quota(user_id, count, now=None):
        return {"used": count}

    monkeypatch.setattr(digest, "enforce_and_consume_quota", fake_quota)
    out = await digest.run_unread_digest({"afterDays": 7}, _Svc())
    md = out["markdown"]
    assert "未讀總數" in md
    assert "按 domain 分組 top 10" in md
    assert "按 label 分組 top 5" in md
