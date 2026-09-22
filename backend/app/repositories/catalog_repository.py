from typing import Any, Literal
from uuid import UUID

from supabase import AsyncClient

SONG_COLUMNS = (
    "id,source_provider,external_id,album_id,title,duration_ms,track_number,"
    "release_date,explicit,cover_url,external_url,preview_url,audio_object_key,"
    "license_name,license_url,can_stream,can_download,status,provider_popularity,"
    "popularity_score,last_synced_at,created_at,updated_at"
)
ALBUM_COLUMNS = (
    "id,source_provider,external_id,title,album_type,cover_url,release_date,"
    "external_url,created_at,updated_at"
)
ARTIST_COLUMNS = (
    "id,source_provider,external_id,name,image_url,external_url,created_at,updated_at"
)
ARTIST_SUMMARY_COLUMNS = "id,source_provider,external_id,name,image_url,external_url"
SONG_ARTIST_COLUMNS = "song_id,artist_id,role,artist_order"
SONG_SORT_FIELDS = frozenset(("release_date", "popularity_score"))


class CatalogDatabaseError(Exception):
    pass


class CatalogRepository:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list_songs(
        self,
        *,
        limit: int,
        offset: int,
        query: str | None,
        artist_id: UUID | None,
        album_id: UUID | None,
        sort_by: Literal["release_date", "popularity_score"],
    ) -> list[dict[str, Any]]:
        try:
            if sort_by not in SONG_SORT_FIELDS:
                raise ValueError("Unsupported song sort field")

            query = query.strip() if query is not None else None
            query = query or None
            song_ids: list[str] | None = None
            if artist_id is not None:
                link_response = await (
                    self._client.table("song_artists")
                    .select("song_id")
                    .eq("artist_id", str(artist_id))
                    .execute()
                )
                song_ids = [row["song_id"] for row in link_response.data]
                if not song_ids:
                    return []

            request = (
                self._client.table("songs").select(SONG_COLUMNS).eq("status", "ready")
            )
            if query:
                request = request.ilike("title", f"%{query}%")
            if album_id is not None:
                request = request.eq("album_id", str(album_id))
            if song_ids is not None:
                request = request.in_("id", song_ids)

            response = await (
                request.order(sort_by, desc=True, nullsfirst=False)
                .range(offset, offset + limit - 1)
                .execute()
            )
            return await self._with_song_relations(response.data)
        except Exception as exc:
            raise CatalogDatabaseError("Catalog database request failed") from exc

    async def get_song(self, song_id: UUID) -> dict[str, Any] | None:
        try:
            response = await (
                self._client.table("songs")
                .select(SONG_COLUMNS)
                .eq("id", str(song_id))
                .eq("status", "ready")
                .limit(1)
                .execute()
            )
            songs = await self._with_song_relations(response.data)
            return songs[0] if songs else None
        except Exception as exc:
            raise CatalogDatabaseError("Catalog database request failed") from exc

    async def list_artists(
        self, *, limit: int, offset: int, query: str | None
    ) -> list[dict[str, Any]]:
        try:
            query = query.strip() if query is not None else None
            query = query or None
            request = self._client.table("artists").select(ARTIST_COLUMNS)
            if query:
                request = request.ilike("name", f"%{query}%")

            response = (
                await request.order("name").range(offset, offset + limit - 1).execute()
            )
            return response.data
        except Exception as exc:
            raise CatalogDatabaseError("Catalog database request failed") from exc

    async def get_artist(self, artist_id: UUID) -> dict[str, Any] | None:
        try:
            response = await (
                self._client.table("artists")
                .select(ARTIST_COLUMNS)
                .eq("id", str(artist_id))
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as exc:
            raise CatalogDatabaseError("Catalog database request failed") from exc

    async def get_album(self, album_id: UUID) -> dict[str, Any] | None:
        try:
            response = await (
                self._client.table("albums")
                .select(ALBUM_COLUMNS)
                .eq("id", str(album_id))
                .limit(1)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as exc:
            raise CatalogDatabaseError("Catalog database request failed") from exc

    async def _with_song_relations(
        self, song_rows: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        if not song_rows:
            return []

        album_ids = sorted(
            {row["album_id"] for row in song_rows if row.get("album_id")}
        )
        song_ids = [row["id"] for row in song_rows]

        albums_by_id: dict[str, dict[str, Any]] = {}
        if album_ids:
            album_response = await (
                self._client.table("albums")
                .select(ALBUM_COLUMNS)
                .in_("id", album_ids)
                .execute()
            )
            albums_by_id = {row["id"]: row for row in album_response.data}

        link_response = await (
            self._client.table("song_artists")
            .select(SONG_ARTIST_COLUMNS)
            .in_("song_id", song_ids)
            .execute()
        )
        links = link_response.data
        artist_ids = sorted({row["artist_id"] for row in links})

        artists_by_id: dict[str, dict[str, Any]] = {}
        if artist_ids:
            artist_response = await (
                self._client.table("artists")
                .select(ARTIST_SUMMARY_COLUMNS)
                .in_("id", artist_ids)
                .execute()
            )
            artists_by_id = {row["id"]: row for row in artist_response.data}

        artists_by_song_id: dict[str, list[dict[str, Any]]] = {
            song_id: [] for song_id in song_ids
        }
        for link in sorted(
            links, key=lambda row: (row["song_id"], row["artist_order"], row["role"])
        ):
            artist = artists_by_id.get(link["artist_id"])
            if artist is None:
                continue
            artists_by_song_id.setdefault(link["song_id"], []).append(
                {
                    **artist,
                    "role": link["role"],
                    "artist_order": link["artist_order"],
                }
            )

        return [
            {
                **song,
                "album": albums_by_id.get(song.get("album_id")),
                "artists": artists_by_song_id.get(song["id"], []),
            }
            for song in song_rows
        ]
