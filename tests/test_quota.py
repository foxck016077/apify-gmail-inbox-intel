import pytest

from src.quota import QuotaExceededError, enforce_and_consume_quota


class FakeStore:
    def __init__(self):
        self.data = {}

    async def get_value(self, key):
        return self.data.get(key)

    async def set_value(self, key, value):
        self.data[key] = value


@pytest.mark.asyncio
async def test_quota_throws_on_101(monkeypatch):
    store = FakeStore()

    class FakeActor:
        @staticmethod
        async def open_key_value_store():
            return store

    import src.quota as quota

    monkeypatch.setattr(quota, "Actor", FakeActor)

    await enforce_and_consume_quota("u1", 100)
    with pytest.raises(QuotaExceededError):
        await enforce_and_consume_quota("u1", 1)
