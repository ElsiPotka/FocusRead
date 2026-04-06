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


def reading_session_key(user_id: str, book_id: str) -> str:
    return build_cache_key("reading-session", user_id, book_id)
