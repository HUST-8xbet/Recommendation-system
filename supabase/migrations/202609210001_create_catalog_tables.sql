create schema if not exists extensions;
create extension if not exists pgcrypto with schema extensions;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = public
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create table public.artists (
  id uuid primary key default extensions.gen_random_uuid(),
  source_provider text not null,
  external_id text not null,
  name text not null,
  image_url text,
  external_url text,
  raw_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint artists_source_provider_external_id_key unique (source_provider, external_id)
);

create table public.albums (
  id uuid primary key default extensions.gen_random_uuid(),
  source_provider text not null,
  external_id text not null,
  title text not null,
  album_type text,
  cover_url text,
  release_date date,
  external_url text,
  raw_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint albums_source_provider_external_id_key unique (source_provider, external_id)
);

create table public.songs (
  id uuid primary key default extensions.gen_random_uuid(),
  source_provider text not null,
  external_id text not null,
  album_id uuid references public.albums(id),
  title text not null,
  duration_ms integer,
  track_number integer,
  release_date date,
  explicit boolean,
  cover_url text,
  external_url text,
  preview_url text,
  audio_object_key text,
  license_name text,
  license_url text,
  can_stream boolean not null default false,
  can_download boolean not null default false,
  status text not null default 'draft',
  provider_popularity numeric,
  popularity_score numeric,
  raw_metadata jsonb not null default '{}'::jsonb,
  last_synced_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint songs_source_provider_external_id_key unique (source_provider, external_id),
  constraint songs_duration_ms_nonnegative check (duration_ms is null or duration_ms >= 0),
  constraint songs_track_number_positive check (track_number is null or track_number > 0),
  constraint songs_popularity_score_range check (
    popularity_score is null or (popularity_score >= 0 and popularity_score <= 1)
  ),
  constraint songs_status_check check (status in ('draft', 'processing', 'ready', 'unavailable'))
);

create table public.song_artists (
  song_id uuid references public.songs(id) on delete cascade,
  artist_id uuid references public.artists(id) on delete cascade,
  role text not null default 'primary',
  artist_order integer not null default 0,
  primary key (song_id, artist_id, role),
  constraint song_artists_artist_order_nonnegative check (artist_order >= 0)
);

create index songs_title_idx on public.songs(title);
create index songs_album_id_idx on public.songs(album_id);
create index songs_status_release_date_idx on public.songs(status, release_date);
create index song_artists_artist_id_idx on public.song_artists(artist_id);
create index albums_title_idx on public.albums(title);
create index artists_name_idx on public.artists(name);

create trigger set_artists_updated_at
before update on public.artists
for each row
execute function public.set_updated_at();

create trigger set_albums_updated_at
before update on public.albums
for each row
execute function public.set_updated_at();

create trigger set_songs_updated_at
before update on public.songs
for each row
execute function public.set_updated_at();

alter table public.artists enable row level security;
alter table public.albums enable row level security;
alter table public.songs enable row level security;
alter table public.song_artists enable row level security;

grant select on public.artists to anon, authenticated;
grant select on public.albums to anon, authenticated;
grant select on public.songs to anon, authenticated;
grant select on public.song_artists to anon, authenticated;

create policy "Public artists are readable"
on public.artists
for select
to anon, authenticated
using (
  exists (
    select 1
    from public.song_artists
    join public.songs on songs.id = song_artists.song_id
    where song_artists.artist_id = artists.id
      and songs.status = 'ready'
  )
);

create policy "Public albums are readable"
on public.albums
for select
to anon, authenticated
using (
  exists (
    select 1
    from public.songs
    where songs.album_id = albums.id
      and songs.status = 'ready'
  )
);

create policy "Ready songs are readable"
on public.songs
for select
to anon, authenticated
using (status = 'ready');

create policy "Public song artists are readable"
on public.song_artists
for select
to anon, authenticated
using (
  exists (
    select 1
    from public.songs
    where songs.id = song_artists.song_id
      and songs.status = 'ready'
  )
);
