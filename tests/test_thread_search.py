import pytest

from src import thread_search


class _Req:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return self._data


class _Threads:
    def __init__(self):
        self.thread_data = {
            "t1": {
                "id": "t1",
                "snippet": "hello",
                "messages": [
                    {
                        "internalDate": "1710000000000",
                        "payload": {
                            "headers": [
                                {"name": "From", "value": "Alice <alice@example.com>"},
                                {"name": "To", "value": "me@example.com"},
                                {"name": "Subject", "value": "S1"},
                            ]
                        },
                    }
                ],
            }
        }

    def list(self, **kwargs):
        return _Req({"threads": [{"id": "t1"}]})

    def get(self, userId, id, format):
        return _Req(self.thread_data[id])


class _Users:
    def __init__(self):
        self._threads = _Threads()

    def threads(self):
        return self._threads


class _Svc:
    def users(self):
        return _Users()


@pytest.mark.asyncio
async def test_thread_search_output_shape(monkeypatch):
    async def fake_quota(user_id, count, now=None):
        return {"used": count, "limit": 100}

    monkeypatch.setattr(thread_search, "enforce_and_consume_quota", fake_quota)
    out = await thread_search.run_thread_search({"query": "in:inbox", "max_results": 5}, _Svc())
    assert out["total"] == 1
    assert out["threads"][0]["id"] == "t1"
    assert out["threads"][0]["from"].startswith("Alice")
