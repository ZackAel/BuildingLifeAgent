import importlib
import dotenv


def test_ask_gemini_without_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: None)
    gemini_api = importlib.reload(importlib.import_module("gemini_api"))
    response = gemini_api.ask_gemini("Hello")
    assert response == gemini_api.MISSING_KEY_MSG
    assert not gemini_api.has_api_key()
