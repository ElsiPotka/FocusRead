from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book, BookStatus
from app.domain.books.repositories import BookRepository
from app.domain.books.value_objects import (
    BookCoverImagePath,
    BookDescription,
    BookDocumentType,
    BookFilePath,
    BookId,
    BookLanguage,
    BookPageCount,
    BookProcessingError,
    BookPublishedYear,
    BookPublisher,
    BookSourceFilename,
    BookSubtitle,
    BookTitle,
    BookTotalChunks,
    BookWordCount,
)
from app.infrastructure.persistence.models.book import BookModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookRepository(BookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, book: Book) -> None:
        model = await self.session.get(BookModel, book.id.value)

        if model is None:
            model = BookModel(
                id=book.id.value,
                owner_user_id=book.owner_user_id.value,
                title=book.title.value,
                subtitle=book.subtitle.value if book.subtitle else None,
                document_type=book.document_type.value,
                description=book.description.value if book.description else None,
                language=book.language.value if book.language else None,
                source_filename=(
                    book.source_filename.value if book.source_filename else None
                ),
                file_path=book.file_path.value,
                cover_image_path=(
                    book.cover_image_path.value if book.cover_image_path else None
                ),
                publisher=book.publisher.value if book.publisher else None,
                published_year=(
                    book.published_year.value if book.published_year else None
                ),
                page_count=book.page_count.value if book.page_count else None,
                word_count=book.word_count.value if book.word_count else None,
                total_chunks=book.total_chunks.value if book.total_chunks else None,
                has_images=book.has_images,
                toc_extracted=book.toc_extracted,
                status=book.status.value,
                processing_error=(
                    book.processing_error.value if book.processing_error else None
                ),
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            self.session.add(model)
            return

        model.owner_user_id = book.owner_user_id.value
        model.title = book.title.value
        model.subtitle = book.subtitle.value if book.subtitle else None
        model.document_type = book.document_type.value
        model.description = book.description.value if book.description else None
        model.language = book.language.value if book.language else None
        model.source_filename = (
            book.source_filename.value if book.source_filename else None
        )
        model.file_path = book.file_path.value
        model.cover_image_path = (
            book.cover_image_path.value if book.cover_image_path else None
        )
        model.publisher = book.publisher.value if book.publisher else None
        model.published_year = (
            book.published_year.value if book.published_year else None
        )
        model.page_count = book.page_count.value if book.page_count else None
        model.word_count = book.word_count.value if book.word_count else None
        model.total_chunks = book.total_chunks.value if book.total_chunks else None
        model.has_images = book.has_images
        model.toc_extracted = book.toc_extracted
        model.status = book.status.value
        model.processing_error = (
            book.processing_error.value if book.processing_error else None
        )
        model.updated_at = book.updated_at

    async def get(self, book_id: BookId) -> Book | None:
        model = await self.session.get(BookModel, book_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_for_owner(
        self, *, book_id: BookId, owner_user_id: UserId
    ) -> Book | None:
        stmt = select(BookModel).where(
            BookModel.id == book_id.value,
            BookModel.owner_user_id == owner_user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_owner(self, *, owner_user_id: UserId) -> list[Book]:
        stmt = (
            select(BookModel)
            .where(BookModel.owner_user_id == owner_user_id.value)
            .order_by(BookModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(model) for model in result.scalars().all()]

    async def delete(self, *, book_id: BookId) -> None:
        model = await self.session.get(BookModel, book_id.value)
        if model is not None:
            await self.session.delete(model)

    @staticmethod
    def _to_entity(model: BookModel) -> Book:
        return Book(
            id=BookId(model.id),
            owner_user_id=UserId(model.owner_user_id),
            title=BookTitle(model.title),
            subtitle=BookSubtitle(model.subtitle) if model.subtitle else None,
            document_type=BookDocumentType(model.document_type),
            description=BookDescription(model.description)
            if model.description
            else None,
            language=BookLanguage(model.language) if model.language else None,
            source_filename=(
                BookSourceFilename(model.source_filename)
                if model.source_filename
                else None
            ),
            file_path=BookFilePath(model.file_path),
            cover_image_path=(
                BookCoverImagePath(model.cover_image_path)
                if model.cover_image_path
                else None
            ),
            publisher=BookPublisher(model.publisher) if model.publisher else None,
            published_year=(
                BookPublishedYear(model.published_year)
                if model.published_year is not None
                else None
            ),
            page_count=(
                BookPageCount(model.page_count)
                if model.page_count is not None
                else None
            ),
            word_count=(
                BookWordCount(model.word_count)
                if model.word_count is not None
                else None
            ),
            total_chunks=(
                BookTotalChunks(model.total_chunks)
                if model.total_chunks is not None
                else None
            ),
            has_images=model.has_images,
            toc_extracted=model.toc_extracted,
            status=BookStatus(model.status),
            processing_error=(
                BookProcessingError(model.processing_error)
                if model.processing_error
                else None
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
