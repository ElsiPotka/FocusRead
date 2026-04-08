from __future__ import annotations

import json
from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, File, Form, Query, Security, UploadFile
from sse_starlette.sse import EventSourceResponse

from app.application.books.use_cases import (
    DeleteBook,
    GetBook,
    GetBookChunk,
    ListBooks,
    ResolveBookChunk,
    UpdateBookMetadata,
    UploadBook,
)
from app.application.common.errors import NotFoundError
from app.domain.auth.value_objects import UserId
from app.domain.books.entities import BookStatus
from app.domain.books.value_objects import BookId
from app.infrastructure.cache.keys import book_processing_channel
from app.infrastructure.cache.redis import get_cache, get_redis
from app.infrastructure.persistence.unit_of_work import get_uow
from app.infrastructure.storage.file_storage import FileStorage, get_file_storage
from app.presentation.api.middleware.auth import get_current_user
from app.presentation.api.schemas.books import (
    BookChunkResponse,
    BookResponse,
    ResolveChunkResponse,
    UpdateBookRequest,
    UploadBookResponse,
)
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)

if TYPE_CHECKING:
    from redis.asyncio import Redis

    from app.domain.auth.entities import User
    from app.infrastructure.cache.redis_cache import RedisCache

router = APIRouter(prefix="/books", tags=["books"])

MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB
PDF_MAGIC_BYTES = b"%PDF"


@router.post("/upload")
async def upload_book(
    file: UploadFile = File(...),
    title: str = Form(...),
    document_type: str = Form(default="book"),
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    storage: FileStorage = Depends(get_file_storage),
) -> APIResponse[UploadBookResponse]:
    if file.content_type not in ("application/pdf", "application/x-pdf"):
        raise NotFoundError("Only PDF files are supported.")

    file_content = await file.read()

    if len(file_content) > MAX_UPLOAD_SIZE:
        raise NotFoundError("File size exceeds the 100MB limit.")

    if not file_content[:5].startswith(PDF_MAGIC_BYTES):
        raise NotFoundError("File does not appear to be a valid PDF.")

    use_case = UploadBook(uow, storage)
    book = await use_case.execute(
        owner_user_id=current_user.id.value,
        title=title,
        source_filename=file.filename or "upload.pdf",
        file_content=file_content,
        document_type=document_type,
    )
    return APIResponse(
        success=True,
        data=UploadBookResponse.from_entity(book),
        message="Book uploaded, processing started",
    )


@router.get("/{book_id}/processing-status")
async def processing_status(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    redis_client: Redis = Depends(get_redis),
) -> EventSourceResponse:
    book = await uow.books.get_for_owner(
        book_id=BookId(book_id),
        owner_user_id=UserId(current_user.id.value),
    )
    if book is None:
        raise NotFoundError("Book not found")

    if book.status in (BookStatus.READY, BookStatus.ERROR):

        async def single_event():
            chunks_ready = book.total_chunks.value if book.total_chunks else 0
            yield {
                "data": json.dumps(
                    {
                        "status": book.status.value,
                        "progress": 100 if book.status == BookStatus.READY else 0,
                        "chunks_ready": chunks_ready,
                        "total_chunks": chunks_ready,
                        "error": (
                            book.processing_error.value
                            if book.processing_error
                            else None
                        ),
                    }
                )
            }

        return EventSourceResponse(single_event())

    async def event_generator():
        pubsub = redis_client.pubsub()
        channel = book_processing_channel(str(book_id))
        await pubsub.subscribe(channel)
        try:
            yield {
                "data": json.dumps(
                    {
                        "status": book.status.value,
                        "progress": 0,
                        "chunks_ready": 0,
                        "total_chunks": None,
                    }
                )
            }

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield {"data": json.dumps(data)}
                    if data.get("status") in ("ready", "error"):
                        break
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    return EventSourceResponse(event_generator())


@router.get("/{book_id}/chunks/resolve")
async def resolve_chunk(
    book_id: UUID,
    word_index: int = Query(..., ge=0),
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ResolveChunkResponse]:
    use_case = ResolveBookChunk(uow)
    result = await use_case.execute(
        book_id=book_id,
        word_index=word_index,
        owner_user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=ResolveChunkResponse(
            chunk_index=result.chunk_index,
            local_offset=result.local_offset,
            start_word_index=result.start_word_index,
            word_count=result.word_count,
        ),
        message="Chunk resolved",
    )


@router.get("/{book_id}/chunks/{chunk_index}")
async def get_book_chunk(
    book_id: UUID,
    chunk_index: int,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[BookChunkResponse]:
    use_case = GetBookChunk(uow, cache)
    chunk = await use_case.execute(
        book_id=book_id,
        chunk_index=chunk_index,
        owner_user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=BookChunkResponse.from_entity(chunk),
        message="Chunk retrieved",
    )


@router.get("")
async def list_books(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[BookResponse]:
    use_case = ListBooks(uow)
    books = await use_case.execute(owner_user_id=current_user.id.value)
    return ListResponse(
        success=True,
        data=[BookResponse.from_entity(book) for book in books],
        count=len(books),
        message="Books retrieved",
    )


@router.get("/{book_id}")
async def get_book(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookResponse]:
    use_case = GetBook(uow)
    book = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=BookResponse.from_entity(book),
        message="Book retrieved",
    )


@router.patch("/{book_id}")
async def update_book(
    book_id: UUID,
    body: UpdateBookRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[BookResponse]:
    use_case = UpdateBookMetadata(uow)
    book = await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
        updates=body.model_dump(exclude_unset=True, mode="python"),
    )
    return APIResponse(
        success=True,
        data=BookResponse.from_entity(book),
        message="Book updated",
    )


@router.delete("/{book_id}")
async def delete_book(
    book_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = DeleteBook(uow)
    await use_case.execute(
        book_id=book_id,
        owner_user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Book deleted")
