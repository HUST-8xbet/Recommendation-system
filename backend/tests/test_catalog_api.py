from datetime import date, datetime, timezone
from typing import Literal
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.routes.catalog import get_catalog_repository
from app.main import app
from app.repositories.catalog_repository import CatalogDatabaseError

SONG_ID = UUID("00000000-0000-4000-8000-000000000001")
ARTIST_ID = UUID("11111111-1111-4111-8111-111111111111")
ALBUM_ID = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1")
NOW = datetime(2026, 9, 21, 9, 0, tzinfo=timezone.utc)


def make_song_row() -> dict[str, object]:
    return {
        "id": str(SONG_ID),
        "source_provider": "demo",
        "external_id": "song-night-bus",
        "album_id": str(ALBUM_ID),
        "title": "Night Bus",
        "duration_ms": 186000,
        "track_number": 1,
        "release_date": "2025-02-14",
        "explicit": False,
        "cover_url": None,
        "external_url": None,
        "preview_url": None,
        "audio_object_key": None,
        "license_name": "Demo metadata only",
        "license_url": None,
        "can_stream": False,
        "can_download": False,
        "status": "ready",
        "provider_popularity": 71,
        "popularity_score": 0.71,
        "last_synced_at": NOW,
        "created_at": NOW,
        "updated_at": NOW,
        "album": {
            "id": str(ALBUM_ID),
            "source_provider": "demo",
            "external_id": "album-city-lights",
            "title": "City Lights",
            "album_type": "album",
            "cover_url": None,
            "release_date": "2025-02-14",
            "external_url": None,
        },
        "artists": [
            {
                "id": str(ARTIST_ID),
                "source_provider": "demo",
                "external_id": "artist-aurora-lane",
                "name": "Aurora Lane",
                "image_url": None,
                "external_url": None,
                "role": "primary",
                "artist_order": 0,
            }
        ],
    }


def make_artist_row() -> dict[str, object]:
    return {
        "id": str(ARTIST_ID),
        "source_provider": "demo",
        "external_id": "artist-aurora-lane",
        "name": "Aurora Lane",
        "image_url": None,
        "external_url": None,
        "created_at": NOW,
        "updated_at": NOW,
    }


def make_album_row() -> dict[str, object]:
    return {
        "id": str(ALBUM_ID),
        "source_provider": "demo",
        "external_id": "album-city-lights",
        "title": "City Lights",
        "album_type": "album",
        "cover_url": None,
        "release_date": date(2025, 2, 14),
        "external_url": None,
        "created_at": NOW,
        "updated_at": NOW,
    }


class FakeCatalogRepository:
    def __init__(self) -> None:
        self.list_songs_kwargs: dict[str, object] | None = None
        self.raise_database_error = False

    async def list_songs(
        self,
        *,
        limit: int,
        offset: int,
        query: str | None,
        artist_id: UUID | None,
        album_id: UUID | None,
        sort_by: Literal["release_date", "popularity_score"],
    ) -> list[dict[str, object]]:
        self.list_songs_kwargs = {
            "limit": limit,
            "offset": offset,
            "query": query,
            "artist_id": artist_id,
            "album_id": album_id,
            "sort_by": sort_by,
        }
        if self.raise_database_error:
            raise CatalogDatabaseError("postgres://user:password@example.invalid/db")
        return [make_song_row()]

    async def get_song(self, song_id: UUID) -> dict[str, object] | None:
        if self.raise_database_error:
            raise CatalogDatabaseError("postgres://user:password@example.invalid/db")
        return make_song_row() if song_id == SONG_ID else None

    async def list_artists(
        self, *, limit: int, offset: int, query: str | None
    ) -> list[dict[str, object]]:
        return [make_artist_row()]

    async def get_artist(self, artist_id: UUID) -> dict[str, object] | None:
        return make_artist_row() if artist_id == ARTIST_ID else None

    async def get_album(self, album_id: UUID) -> dict[str, object] | None:
        return make_album_row() if album_id == ALBUM_ID else None


@pytest.fixture
def fake_repository() -> FakeCatalogRepository:
    repository = FakeCatalogRepository()

    async def override_catalog_repository() -> FakeCatalogRepository:
        return repository

    app.dependency_overrides[get_catalog_repository] = override_catalog_repository
    return repository


@pytest.fixture(autouse=True)
def clear_overrides() -> None:
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


async def get_client() -> AsyncClient:
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.anyio
async def test_list_songs(fake_repository: FakeCatalogRepository) -> None:
    async with await get_client() as client:
        response = await client.get("/api/v1/songs")

    assert response.status_code == 200
    body = response.json()
    assert body[0]["id"] == str(SONG_ID)
    assert body[0]["album"]["title"] == "City Lights"
    assert body[0]["artists"][0]["name"] == "Aurora Lane"
    assert "raw_metadata" not in body[0]
    assert fake_repository.list_songs_kwargs == {
        "limit": 20,
        "offset": 0,
        "query": None,
        "artist_id": None,
        "album_id": None,
        "sort_by": "release_date",
    }


@pytest.mark.anyio
async def test_list_songs_filter_search(fake_repository: FakeCatalogRepository) -> None:
    async with await get_client() as client:
        response = await client.get(
            f"/api/v1/songs?query=Night&artist_id={ARTIST_ID}&album_id={ALBUM_ID}"
            "&limit=10&offset=5&sort_by=popularity_score"
        )

    assert response.status_code == 200
    assert fake_repository.list_songs_kwargs == {
        "limit": 10,
        "offset": 5,
        "query": "Night",
        "artist_id": ARTIST_ID,
        "album_id": ALBUM_ID,
        "sort_by": "popularity_score",
    }


@pytest.mark.anyio
async def test_whitespace_search_is_treated_as_empty(
    fake_repository: FakeCatalogRepository,
) -> None:
    async with await get_client() as client:
        response = await client.get("/api/v1/songs?query=%20%20")

    assert response.status_code == 200
    assert fake_repository.list_songs_kwargs is not None
    assert fake_repository.list_songs_kwargs["query"] is None


@pytest.mark.anyio
async def test_sort_by_is_allowlisted(fake_repository: FakeCatalogRepository) -> None:
    async with await get_client() as client:
        response = await client.get("/api/v1/songs?sort_by=title")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_song_detail(fake_repository: FakeCatalogRepository) -> None:
    async with await get_client() as client:
        response = await client.get(f"/api/v1/songs/{SONG_ID}")

    assert response.status_code == 200
    assert response.json()["title"] == "Night Bus"


@pytest.mark.anyio
async def test_song_not_found(fake_repository: FakeCatalogRepository) -> None:
    missing_id = "00000000-0000-4000-8000-000000000099"
    async with await get_client() as client:
        response = await client.get(f"/api/v1/songs/{missing_id}")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_invalid_uuid_returns_422(fake_repository: FakeCatalogRepository) -> None:
    async with await get_client() as client:
        response = await client.get("/api/v1/songs/not-a-uuid")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_limit_out_of_range_returns_422(
    fake_repository: FakeCatalogRepository,
) -> None:
    async with await get_client() as client:
        response = await client.get("/api/v1/songs?limit=101")

    assert response.status_code == 422


@pytest.mark.anyio
async def test_database_failure_is_sanitized(
    fake_repository: FakeCatalogRepository,
) -> None:
    fake_repository.raise_database_error = True

    async with await get_client() as client:
        response = await client.get("/api/v1/songs")

    assert response.status_code == 503
    assert response.json() == {"detail": "Catalog database request failed"}
    assert "password" not in response.text
    assert "postgres://" not in response.text
