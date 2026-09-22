from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes import catalog
from app.core import config
from app.core.config import Settings, get_settings
from app.db import supabase
from app.main import app


def test_settings_use_an_absolute_backend_env_file_path() -> None:
    assert config.BACKEND_DIR == Path(config.__file__).resolve().parents[2]
    assert Settings.model_config["env_file"] == config.BACKEND_DIR / ".env"
    assert Settings.model_config["env_file_encoding"] == "utf-8"
    assert Settings.model_config["extra"] == "ignore"


def test_environment_variables_override_temporary_env_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        "SUPABASE_URL=http://env-file.invalid\nSUPABASE_PUBLISHABLE_KEY=file-key\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("SUPABASE_URL", "http://environment.invalid")
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "environment-key")

    settings = Settings(_env_file=env_file)

    assert settings.supabase_url == "http://environment.invalid"
    assert settings.supabase_publishable_key == "environment-key"


def test_settings_can_read_a_temporary_env_file_without_repository_env(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(
        "SUPABASE_URL=http://temporary.invalid\n"
        "SUPABASE_PUBLISHABLE_KEY=temporary-key\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)

    settings = Settings(_env_file=env_file)

    assert settings.supabase_url == "http://temporary.invalid"
    assert settings.supabase_publishable_key == "temporary-key"


def test_get_settings_cache_is_clearable_when_environment_changes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(config, "Settings", lambda: Settings(_env_file=None))
    monkeypatch.setenv("APP_NAME", "test-before-cache-clear")
    get_settings.cache_clear()
    before = get_settings()

    monkeypatch.setenv("APP_NAME", "test-after-cache-clear")
    get_settings.cache_clear()
    after = get_settings()

    assert before.app_name == "test-before-cache-clear"
    assert after.app_name == "test-after-cache-clear"
    get_settings.cache_clear()


@pytest.mark.anyio
async def test_missing_supabase_configuration_is_safe(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    missing = Settings(_env_file=None)
    missing.supabase_url = None
    missing.supabase_publishable_key = None
    monkeypatch.setattr(supabase, "get_settings", lambda: missing)
    monkeypatch.setattr(supabase, "_client", None)

    with pytest.raises(RuntimeError, match="configuration is missing"):
        await supabase.get_supabase_client()


@pytest.mark.anyio
async def test_catalog_returns_generic_error_when_configuration_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def raise_missing_configuration() -> None:
        raise RuntimeError("Supabase backend configuration is missing")

    monkeypatch.setattr(catalog, "get_supabase_client", raise_missing_configuration)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/api/v1/songs")

    assert response.status_code == 503
    assert response.json() == {"detail": "Catalog database request failed"}
    assert "SUPABASE" not in response.text
