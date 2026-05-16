import pytest

from src import summarizer


class _Req:
    def __init__(self, data):
        self._data = data

    def execute(self):
        return self._data


class _Threads:
    def list(self, **kwargs):
        return _Req({"threads": [{"id": "t1"}]})

    def get(self, userId, id, format):
        return _Req({"id": "t1", "messages": [{"id": "m1"}]})


class _Messages:
    def get(self, userId, id, format):
        return _Req({"payload": {"body": {"data": "TOKEN_ABC_SHOULD_NOT_BE_LOGGED"}}})


class _Users:
    def __init__(self):
        self._threads = _Threads()
        self._messages = _Messages()

    def threads(self):
        return self._threads

    def messages(self):
        return self._messages


class _Svc:
    def users(self):
        return _Users()


class _Resp:
    output_text = "gist"
    usage = type("U", (), {"input_tokens": 100, "output_tokens": 20})


class _Responses:
    def __init__(self):
        self.last_input = None

    async def create(self, **kwargs):
        self.last_input = kwargs["input"]
        return _Resp()


class _FakeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.responses = _Responses()


@pytest.mark.asyncio
async def test_summarizer_uses_input_key_and_builds_prompt(monkeypatch):
    async def fake_quota(user_id, count, now=None):
        return {"used": count}

    monkeypatch.setattr(summarizer, "enforce_and_consume_quota", fake_quota)
    monkeypatch.setattr(summarizer, "AsyncOpenAI", _FakeClient)

    out = await summarizer.run_summarizer(
        {"openai_api_key": "sk-test", "summary_model": "gpt-4o-mini"},
        _Svc(),
    )
    assert out["summaries"][0]["thread_id"] == "t1"
    assert out["summaries"][0]["cost_usd"] > 0
