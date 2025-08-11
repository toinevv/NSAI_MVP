import importlib
import sys


def test_gpt4v_client_uses_env_config(monkeypatch):
    # Ensure fresh settings import
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GPT4V_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("MAX_TOKENS_PER_REQUEST", "1024")
    monkeypatch.setenv("GPT4V_TEMPERATURE", "0.2")
    monkeypatch.setenv("GPT4V_IMAGE_DETAIL", "low")

    # Reload settings to pick up env
    from app.core import config as config_module
    importlib.reload(config_module)

    # Ensure gpt4v_client sees the reloaded settings
    import app.services.analysis.gpt4v_client as gpt4v_client_module
    importlib.reload(gpt4v_client_module)
    GPT4VClient = gpt4v_client_module.GPT4VClient

    client = GPT4VClient()

    assert client.model == "gpt-4o-mini"
    assert client.max_tokens == 1024
    assert abs(client.temperature - 0.2) < 1e-6
    assert client.image_detail == "low"

    # Build a message and verify the detail propagates
    frame = {"image_base64": "ZmFrZQ==", "timestamp_formatted": "00:00"}
    messages = client._prepare_messages([frame], "sys", "user")
    # Find the image_url content
    image_items = [c for c in messages[1]["content"] if c.get("type") == "image_url"]
    assert len(image_items) == 1
    assert image_items[0]["image_url"]["detail"] == "low"


