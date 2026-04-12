from app.infrastructure.config.settings import settings


def build_cache_key(*parts: str | int) -> str:
    normalized_parts = [
        settings.REDIS_KEY_PREFIX,
        *[str(part).strip(":") for part in parts],
    ]
    return ":".join(normalized_parts)


def book_metadata_key(book_id: str) -> str:
    return build_cache_key("book", book_id, "metadata")


def book_chunk_key(book_id: str, chunk_index: int) -> str:
    return build_cache_key("book", book_id, "chunk", chunk_index)


def book_processing_channel(book_id: str) -> str:
    return build_cache_key("book", book_id, "processing")


def reading_session_key(user_id: str, book_id: str) -> str:
    return build_cache_key("reading-session", user_id, book_id)


def book_ownership_key(user_id: str, book_id: str) -> str:
    return build_cache_key("book-ownership", user_id, book_id)


def theme_key(theme_id: str) -> str:
    return build_cache_key("theme", theme_id)


def user_active_theme_key(user_id: str) -> str:
    return build_cache_key("theme", "active", user_id)


def marketplace_themes_key(sort_by: str, page: int) -> str:
    return build_cache_key("theme", "marketplace", sort_by, page)
