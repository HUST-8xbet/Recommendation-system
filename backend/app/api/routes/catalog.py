from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.db.supabase import get_supabase_client
from app.models.catalog import AlbumResponse, ArtistResponse, SongResponse
from app.repositories.catalog_repository import CatalogDatabaseError, CatalogRepository
from app.services.catalog_service import CatalogNotFoundError, CatalogService

router = APIRouter(tags=["catalog"])


async def get_catalog_repository() -> CatalogRepository:
    try:
        return CatalogRepository(await get_supabase_client())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Catalog database request failed",
        ) from exc


async def get_catalog_service(
    repository: Annotated[CatalogRepository, Depends(get_catalog_repository)],
) -> CatalogService:
    return CatalogService(repository)


def _handle_catalog_error(exc: Exception) -> None:
    if isinstance(exc, CatalogNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    if isinstance(exc, CatalogDatabaseError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Catalog database request failed",
        ) from exc
    raise exc


@router.get("/songs", response_model=list[SongResponse])
async def list_songs(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    query: Annotated[str | None, Query(min_length=1)] = None,
    artist_id: UUID | None = None,
    album_id: UUID | None = None,
    sort_by: Literal["release_date", "popularity_score"] = "release_date",
) -> list[SongResponse]:
    try:
        return await service.list_songs(
            limit=limit,
            offset=offset,
            query=query,
            artist_id=artist_id,
            album_id=album_id,
            sort_by=sort_by,
        )
    except Exception as exc:
        _handle_catalog_error(exc)
        raise


@router.get("/songs/{song_id}", response_model=SongResponse)
async def get_song(
    song_id: UUID,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> SongResponse:
    try:
        return await service.get_song(song_id)
    except Exception as exc:
        _handle_catalog_error(exc)
        raise


@router.get("/artists", response_model=list[ArtistResponse])
async def list_artists(
    service: Annotated[CatalogService, Depends(get_catalog_service)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    query: Annotated[str | None, Query(min_length=1)] = None,
) -> list[ArtistResponse]:
    try:
        return await service.list_artists(limit=limit, offset=offset, query=query)
    except Exception as exc:
        _handle_catalog_error(exc)
        raise


@router.get("/artists/{artist_id}", response_model=ArtistResponse)
async def get_artist(
    artist_id: UUID,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> ArtistResponse:
    try:
        return await service.get_artist(artist_id)
    except Exception as exc:
        _handle_catalog_error(exc)
        raise


@router.get("/albums/{album_id}", response_model=AlbumResponse)
async def get_album(
    album_id: UUID,
    service: Annotated[CatalogService, Depends(get_catalog_service)],
) -> AlbumResponse:
    try:
        return await service.get_album(album_id)
    except Exception as exc:
        _handle_catalog_error(exc)
        raise
