"""Settings tests. They use a temporary .env so nothing depends on a local one."""

import os

from app.config import get_settings, load_dotenv


def test_load_dotenv_ignores_a_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("UNTOUCHED", "yes")
    assert load_dotenv(tmp_path / "missing.env") is None
    assert os.environ["UNTOUCHED"] == "yes"


def test_load_dotenv_fills_only_unset_keys(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n"
        "# comment\n"
        "not a pair\n"
        "NEW_KEY=from-file\n"
        "EXISTING=from-file\n"
        "  SPACED = value \n",
        encoding="utf-8",
    )
    monkeypatch.setenv("EXISTING", "already")
    monkeypatch.delenv("NEW_KEY", raising=False)
    monkeypatch.delenv("SPACED", raising=False)

    load_dotenv(env_file)

    assert os.environ["NEW_KEY"] == "from-file"
    assert os.environ["EXISTING"] == "already"
    assert os.environ["SPACED"] == "value"


def test_get_settings_reads_the_environment(monkeypatch):
    monkeypatch.setattr("app.config.load_dotenv", lambda path=None: None)
    monkeypatch.setenv("OPENFDA_MODE", " Live ")
    monkeypatch.setenv("OPENFDA_API_KEY", "secret")
    monkeypatch.setenv("OPENFDA_BASE_URL", "https://fda.example")
    monkeypatch.setenv("OPENFDA_TIMEOUT_SECONDS", "3.5")

    settings = get_settings()

    assert settings.openfda_mode == "live"
    assert settings.openfda_api_key == "secret"
    assert settings.openfda_base_url == "https://fda.example"
    assert settings.openfda_timeout == 3.5


def test_get_settings_uses_defaults_when_unset(monkeypatch):
    monkeypatch.setattr("app.config.load_dotenv", lambda path=None: None)
    for name in ("OPENFDA_MODE", "OPENFDA_API_KEY", "OPENFDA_BASE_URL", "OPENFDA_TIMEOUT_SECONDS"):
        monkeypatch.delenv(name, raising=False)

    settings = get_settings()

    assert settings.openfda_mode == "fixture"
    assert settings.openfda_api_key == ""
    assert settings.openfda_base_url == "https://api.fda.gov"
    assert settings.openfda_timeout == 10.0
