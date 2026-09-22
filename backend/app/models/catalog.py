from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class AlbumSummary(BaseModel):
    id: UUID
    source_provider: str
    external_id: str
    album_id: UUID | None = None
    title: str
    album_type: str | None = None
    cover_url: str | None = None
    release_date: date | None = None
    external_url: str | None = None


class ArtistSummary(BaseModel):
    id: UUID
    source_provider: str
    external_id: str
    name: str
    image_url: str | None = None
    external_url: str | None = None
    role: str | None = None
    artist_order: int | None = None


class SongResponse(BaseModel):
    id: UUID
    source_provider: str
    external_id: str
    title: str
    duration_ms: int | None = None
    track_number: int | None = None
    release_date: date | None = None
    explicit: bool | None = None
    cover_url: str | None = None
    external_url: str | None = None
    preview_url: str | None = None
    audio_object_key: str | None = None
    license_name: str | None = None
    license_url: str | None = None
    can_stream: bool
    can_download: bool
    status: str
    provider_popularity: float | None = None
    popularity_score: float | None = None
    last_synced_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    album: AlbumSummary | None = None
    artists: list[ArtistSummary]


class ArtistResponse(BaseModel):
    id: UUID
    source_provider: str
    external_id: str
    name: str
    image_url: str | None = None
    external_url: str | None = None
    created_at: datetime
    updated_at: datetime


class AlbumResponse(BaseModel):
    id: UUID
    source_provider: str
    external_id: str
    title: str
    album_type: str | None = None
    cover_url: str | None = None
    release_date: date | None = None
    external_url: str | None = None
    created_at: datetime
    updated_at: datetime
