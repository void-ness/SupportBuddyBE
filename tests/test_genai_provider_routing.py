import pytest

from managers.genai_manager import GenAIManager


@pytest.mark.asyncio
async def test_generate_routes_to_provider(monkeypatch):
    calls = []

    class FakeProvider:
        async def generate_text(self, *, prompt, system_prompt=None, model_name=None, params=None):
            calls.append((prompt, system_prompt, model_name))
            return "ok"

        async def generate_json(self, *, prompt, system_prompt=None, model_name=None, schema=None, params=None):
            return {"message": "m", "subject": "s"}

    # Patch factory
    monkeypatch.setattr(
        "managers.genai_manager.get_provider",
        lambda name: FakeProvider(),
    )

    out = await GenAIManager.generate("hi", "sys", provider="amazon")
    assert out == "ok"
    assert calls == [("hi", "sys", None)]


@pytest.mark.asyncio
async def test_generate_reminder_mail_data_uses_generate_json(monkeypatch):
    class FakeProvider:
        async def generate_text(self, **kwargs):
            raise AssertionError("should not be called")

        async def generate_json(self, **kwargs):
            return {"message": "hello", "subject": "sub"}

    monkeypatch.setattr(
        "managers.genai_manager.get_provider",
        lambda name: FakeProvider(),
    )

    msg, subj = await GenAIManager.generate_reminder_mail_data(
        last_journal_entry="x",
        inactive_days=2,
        provider="amazon",
    )
    assert msg == "hello"
    assert subj == "sub"
