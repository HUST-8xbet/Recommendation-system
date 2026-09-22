insert into public.artists (id, source_provider, external_id, name, image_url, external_url, raw_metadata)
values
  ('11111111-1111-4111-8111-111111111111', 'demo', 'artist-aurora-lane', 'Aurora Lane', null, null, '{"seed": true}'::jsonb),
  ('22222222-2222-4222-8222-222222222222', 'demo', 'artist-neon-river', 'Neon River', null, null, '{"seed": true}'::jsonb),
  ('33333333-3333-4333-8333-333333333333', 'demo', 'artist-midnight-yard', 'Midnight Yard', null, null, '{"seed": true}'::jsonb)
on conflict (source_provider, external_id) do update
set
  name = excluded.name,
  image_url = excluded.image_url,
  external_url = excluded.external_url,
  raw_metadata = excluded.raw_metadata;

insert into public.albums (id, source_provider, external_id, title, album_type, cover_url, release_date, external_url, raw_metadata)
values
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'demo', 'album-city-lights', 'City Lights', 'album', null, '2025-02-14', null, '{"seed": true}'::jsonb),
  ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'demo', 'album-soft-horizon', 'Soft Horizon', 'ep', null, '2025-05-30', null, '{"seed": true}'::jsonb)
on conflict (source_provider, external_id) do update
set
  title = excluded.title,
  album_type = excluded.album_type,
  cover_url = excluded.cover_url,
  release_date = excluded.release_date,
  external_url = excluded.external_url,
  raw_metadata = excluded.raw_metadata;

insert into public.songs (
  id,
  source_provider,
  external_id,
  album_id,
  title,
  duration_ms,
  track_number,
  release_date,
  explicit,
  cover_url,
  external_url,
  preview_url,
  audio_object_key,
  license_name,
  license_url,
  can_stream,
  can_download,
  status,
  provider_popularity,
  popularity_score,
  raw_metadata,
  last_synced_at
)
values
  ('00000000-0000-4000-8000-000000000001', 'demo', 'song-night-bus', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'Night Bus', 186000, 1, '2025-02-14', false, null, null, null, null, 'Demo metadata only', null, false, false, 'ready', 71, 0.71, '{"seed": true, "mood": "late-night"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000002', 'demo', 'song-glass-avenue', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'Glass Avenue', 202000, 2, '2025-02-14', false, null, null, null, null, 'Demo metadata only', null, false, false, 'ready', 66, 0.66, '{"seed": true, "mood": "bright"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000003', 'demo', 'song-parking-lot-stars', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa1', 'Parking Lot Stars', 211000, 3, '2025-02-14', false, null, null, null, null, 'Demo metadata only', null, false, false, 'ready', 59, 0.59, '{"seed": true, "mood": "dreamy"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000004', 'demo', 'song-blue-kitchen', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'Blue Kitchen', 178000, 1, '2025-05-30', false, null, null, null, null, 'Demo metadata only', null, false, false, 'ready', 54, 0.54, '{"seed": true, "mood": "warm"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000005', 'demo', 'song-paper-sun', 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaa2', 'Paper Sun', 194000, 2, '2025-05-30', false, null, null, null, null, 'Demo metadata only', null, false, false, 'ready', 62, 0.62, '{"seed": true, "mood": "soft"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000006', 'demo', 'song-unreleased-sketch', null, 'Unreleased Sketch', 164000, null, null, false, null, null, null, null, 'Demo metadata only', null, false, false, 'draft', 12, 0.12, '{"seed": true, "note": "not public because status is draft"}'::jsonb, now()),
  ('00000000-0000-4000-8000-000000000007', 'demo', 'song-processing-preview', null, 'Processing Preview', 172000, null, null, false, null, null, null, null, 'Demo metadata only', null, false, false, 'processing', 8, 0.08, '{"seed": true, "note": "not public while processing"}'::jsonb, now())
on conflict (source_provider, external_id) do update
set
  album_id = excluded.album_id,
  title = excluded.title,
  duration_ms = excluded.duration_ms,
  track_number = excluded.track_number,
  release_date = excluded.release_date,
  explicit = excluded.explicit,
  cover_url = excluded.cover_url,
  external_url = excluded.external_url,
  preview_url = excluded.preview_url,
  audio_object_key = excluded.audio_object_key,
  license_name = excluded.license_name,
  license_url = excluded.license_url,
  can_stream = excluded.can_stream,
  can_download = excluded.can_download,
  status = excluded.status,
  provider_popularity = excluded.provider_popularity,
  popularity_score = excluded.popularity_score,
  raw_metadata = excluded.raw_metadata,
  last_synced_at = excluded.last_synced_at;

insert into public.song_artists (song_id, artist_id, role, artist_order)
values
  ('00000000-0000-4000-8000-000000000001', '11111111-1111-4111-8111-111111111111', 'primary', 0),
  ('00000000-0000-4000-8000-000000000002', '11111111-1111-4111-8111-111111111111', 'primary', 0),
  ('00000000-0000-4000-8000-000000000003', '22222222-2222-4222-8222-222222222222', 'primary', 0),
  ('00000000-0000-4000-8000-000000000004', '33333333-3333-4333-8333-333333333333', 'primary', 0),
  ('00000000-0000-4000-8000-000000000005', '33333333-3333-4333-8333-333333333333', 'primary', 0),
  ('00000000-0000-4000-8000-000000000005', '11111111-1111-4111-8111-111111111111', 'featured', 1),
  ('00000000-0000-4000-8000-000000000006', '22222222-2222-4222-8222-222222222222', 'primary', 0)
on conflict (song_id, artist_id, role) do update
set artist_order = excluded.artist_order;
