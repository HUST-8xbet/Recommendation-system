from __future__ import annotations

import os
from urllib.parse import urlparse
from uuid import UUID

import httpx
import pytest
from httpx import ASGITransport, AsyncClient
from supabase import AsyncClient as SupabaseAsyncClient
from supabase import acreate_client

from app.api.routes.catalog import get_catalog_repository
from app.main import app
from app.repositories.catalog_repository import CatalogRepository

READY_SONG_COUNT = 5
ARTIST_AURORA = UUID("11111111-1111-4111-8111-111111111111")
ARTIST_MIDNIGHT = UUID("33333333-3333-4333-8333-333333333333")
ALBUM_CITY_LIGHTS = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1")
MISSING_SONG = "00000000-0000-4000-8000-000000000099"


def _local_supabase_settings() -> tuple[str, str] | None:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
    if not url or not key:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in {
        "127.0.0.1",
        "localhost",
        "::1",
    }:
        return None
    return url, key


@pytest.fixture
async def local_client() -> AsyncClient:
    settings = _local_supabase_settings()
    if settings is None:
        pytest.skip("local Supabase credentials were not supplied")

    url, key = settings
    try:
        async with httpx.AsyncClient() as probe:
            response = await probe.get(f"{url}/rest/v1/", timeout=1)
            response.raise_for_status()
        supabase_client: SupabaseAsyncClient = await acreate_client(url, key)
    except (httpx.HTTPError, OSError) as exc:
        pytest.skip(f"local Supabase is not running: {exc.__class__.__name__}")

    async def override_repository() -> CatalogRepository:
        return CatalogRepository(supabase_client)

    app.dependency_overrides[get_catalog_repository] = override_repository
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")
    try:
        yield client
    finally:
        await client.aclose()
        app.dependency_overrides.pop(get_catalog_repository, None)


@pytest.mark.integration
@pytest.mark.anyio
async def test_local_catalog_gate(local_client: AsyncClient) -> None:
    response = await local_client.get("/api/v1/songs?limit=5")
    assert response.status_code == 200
    songs = response.json()
    assert len(songs) == READY_SONG_COUNT
    assert all(song["status"] == "ready" for song in songs)
    assert all("unreleased" not in song["title"].lower() for song in songs)
    assert all("processing" not in song["title"].lower() for song in songs)

    detail = await local_client.get(
        "/api/v1/songs/00000000-0000-4000-8000-000000000005"
    )
    assert detail.status_code == 200
    assert detail.json()["album"]["title"] == "Soft Horizon"
    assert [artist["id"] for artist in detail.json()["artists"]] == [
        str(ARTIST_MIDNIGHT),
        str(ARTIST_AURORA),
    ]

    assert len((await local_client.get("/api/v1/songs?limit=2")).json()) == 2
    assert len((await local_client.get("/api/v1/songs?limit=1&offset=1")).json()) == 1
    assert (
        len((await local_client.get(f"/api/v1/songs?artist_id={ARTIST_AURORA}")).json())
        == 3
    )
    assert (
        len(
            (
                await local_client.get(f"/api/v1/songs?album_id={ALBUM_CITY_LIGHTS}")
            ).json()
        )
        == 3
    )
    assert len((await local_client.get("/api/v1/songs?query=Night Bus")).json()) == 1
    assert (await local_client.get(f"/api/v1/songs/{MISSING_SONG}")).status_code == 404
