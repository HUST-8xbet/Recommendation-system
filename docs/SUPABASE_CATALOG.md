# Supabase Catalog

This project stores database schema changes as SQL migrations under `supabase/migrations`.
Do not create tables from FastAPI startup code.

## Run Migrations Locally

Install the Supabase CLI and make sure Docker is available, then run:

```bash
supabase start
supabase db reset
```

`supabase db reset` only targets the local Supabase database started by the CLI. Do not use reset against a cloud project.

## Run Seed Locally

The local reset command applies migrations and then runs `supabase/seed.sql`. To apply only seed data to an already running local database:

```bash
psql "postgresql://postgres:postgres@127.0.0.1:54322/postgres" -f supabase/seed.sql
```

The seed catalog uses fictional demo metadata and leaves `preview_url` as `null`.

## Apply To Supabase Cloud

Only after reviewing the migration and confirming the target project:

```bash
supabase link --project-ref <project-ref>
supabase db push
```

Do not run destructive reset commands against the cloud database. Confirm the project reference before pushing.
Apply seed data to cloud only after approval, either through the Supabase SQL editor or a reviewed `psql` command using a secure connection string outside Git and chat.

## Rollback

Do not edit a migration that has already been applied. Roll back by creating a new migration that reverses the change, for example:

```bash
supabase migration new rollback_catalog_change
```

Then add SQL such as `drop policy`, `drop trigger`, `drop table`, or corrective `alter table` statements in dependency order.

## Access Model

The catalog migration enables RLS for `artists`, `albums`, `songs`, and `song_artists`.
`anon` and `authenticated` receive `SELECT` only. Songs are public only when `status = 'ready'`; related artists, albums, and song-artist links are visible only when connected to ready songs.
Future backend catalog access should live under `backend/app/db/` or repositories and use async database clients; SQL schema changes should remain in migrations.
