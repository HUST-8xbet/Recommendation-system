from supabase import AsyncClient, acreate_client

from app.core.config import get_settings

_client: AsyncClient | None = None


async def get_supabase_client() -> AsyncClient:
    global _client

    if _client is not None:
        return _client

    settings = get_settings()
    if not settings.supabase_url or not settings.supabase_publishable_key:
        raise RuntimeError("Supabase backend configuration is missing")

    _client = await acreate_client(
        settings.supabase_url, settings.supabase_publishable_key
    )
    return _client
