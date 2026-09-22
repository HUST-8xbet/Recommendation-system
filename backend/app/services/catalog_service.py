from typing import Literal
from uuid import UUID

from app.models.catalog import AlbumResponse, ArtistResponse, SongResponse
from app.repositories.catalog_repository import CatalogRepository


class CatalogNotFoundError(Exception):
    pass


def _normalize_query(query: str | None) -> str | None:
    normalized = query.strip() if query is not None else None
    return normalized or None


class CatalogService:
    def __init__(self, repository: CatalogRepository) -> None:
        self._repository = repository

    async def list_songs(
        self,
        *,
        limit: int,
        offset: int,
        query: str | None,
        artist_id: UUID | None,
        album_id: UUID | None,
        sort_by: Literal["release_date", "popularity_score"],
    ) -> list[SongResponse]:
        rows = await self._repository.list_songs(
            limit=limit,
            offset=offset,
            query=_normalize_query(query),
            artist_id=artist_id,
            album_id=album_id,
            sort_by=sort_by,
        )
        return [SongResponse.model_validate(row) for row in rows]

    async def get_song(self, song_id: UUID) -> SongResponse:
        row = await self._repository.get_song(song_id)
        if row is None:
            raise CatalogNotFoundError("Song not found")
        return SongResponse.model_validate(row)

    async def list_artists(
        self, *, limit: int, offset: int, query: str | None
    ) -> list[ArtistResponse]:
        rows = await self._repository.list_artists(
            limit=limit, offset=offset, query=_normalize_query(query)
        )
        return [ArtistResponse.model_validate(row) for row in rows]

    async def get_artist(self, artist_id: UUID) -> ArtistResponse:
        row = await self._repository.get_artist(artist_id)
        if row is None:
            raise CatalogNotFoundError("Artist not found")
        return ArtistResponse.model_validate(row)

    async def get_album(self, album_id: UUID) -> AlbumResponse:
        row = await self._repository.get_album(album_id)
        if row is None:
            raise CatalogNotFoundError("Album not found")
        return AlbumResponse.model_validate(row)
