from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import or_, select

from app.domain.auth.value_objects import UserId
from app.domain.book_asset.value_objects import BookAssetId, ProcessingStatus
from app.domain.books.entities import Book
from app.domain.books.filter import BookFilter, BookSortField, SortDirection
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
from app.domain.library_item.value_objects import AccessStatus
from app.infrastructure.persistence.models.book import BookModel
from app.infrastructure.persistence.models.book_asset import BookAssetModel
from app.infrastructure.persistence.models.library_item import LibraryItemModel
from app.infrastructure.persistence.repositories._compat import (
    DEFAULT_ASSET_FORMAT,
    DEFAULT_STORAGE_BACKEND,
    build_placeholder_sha,
    detect_file_size_bytes,
    detect_mime_type,
    detect_original_filename,
    ensure_library_item,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyBookRepository(BookRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, book: Book) -> None:
        asset_model = await self.session.get(
            BookAssetModel, book.primary_asset_id.value
        )
        storage_key = book._file_path.value if book._file_path is not None else None
        source_filename = (
            book.source_filename.value if book.source_filename is not None else None
        )

        if asset_model is None:
            resolved_storage_key = storage_key or f"books/{book.id.value}.pdf"
            asset_model = BookAssetModel(
                id=book.primary_asset_id.value,
                sha256=build_placeholder_sha(book_id=book.id.value),
                format=DEFAULT_ASSET_FORMAT,
                mime_type=detect_mime_type(
                    source_filename=source_filename,
                    storage_key=resolved_storage_key,
                ),
                file_size_bytes=detect_file_size_bytes(
                    storage_key=resolved_storage_key
                ),
                storage_backend=DEFAULT_STORAGE_BACKEND,
                storage_key=resolved_storage_key,
                original_filename=detect_original_filename(
                    source_filename=source_filename,
                    storage_key=resolved_storage_key,
                ),
                created_by_user_id=(
                    book.created_by_user_id.value
                    if book.created_by_user_id is not None
                    else None
                ),
                processing_status=book.status.value,
                processing_error=(
                    book.processing_error.value
                    if book.processing_error is not None
                    else None
                ),
                page_count=book.page_count.value if book.page_count else None,
                word_count=book.word_count.value if book.word_count else None,
                total_chunks=book.total_chunks.value if book.total_chunks else None,
                has_images=book.has_images,
                toc_extracted=book.toc_extracted,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            self.session.add(asset_model)
        else:
            if storage_key is not None:
                asset_model.storage_key = storage_key
            if source_filename is not None:
                asset_model.original_filename = source_filename
                asset_model.mime_type = detect_mime_type(
                    source_filename=source_filename,
                    storage_key=asset_model.storage_key,
                )
            asset_model.created_by_user_id = (
                book.created_by_user_id.value
                if book.created_by_user_id is not None
                else None
            )
            asset_model.processing_status = book.status.value
            asset_model.processing_error = (
                book.processing_error.value
                if book.processing_error is not None
                else None
            )
            asset_model.page_count = book.page_count.value if book.page_count else None
            asset_model.word_count = book.word_count.value if book.word_count else None
            asset_model.total_chunks = (
                book.total_chunks.value if book.total_chunks else None
            )
            asset_model.has_images = book.has_images
            asset_model.toc_extracted = book.toc_extracted
            asset_model.updated_at = book.updated_at

        model = await self.session.get(BookModel, book.id.value)
        if model is None:
            model = BookModel(
                id=book.id.value,
                primary_asset_id=book.primary_asset_id.value,
                created_by_user_id=(
                    book.created_by_user_id.value
                    if book.created_by_user_id is not None
                    else None
                ),
                title=book.title.value,
                subtitle=book.subtitle.value if book.subtitle else None,
                document_type=book.document_type.value,
                description=book.description.value if book.description else None,
                language=book.language.value if book.language else None,
                cover_image_path=(
                    book.cover_image_path.value if book.cover_image_path else None
                ),
                publisher=book.publisher.value if book.publisher else None,
                published_year=(
                    book.published_year.value if book.published_year else None
                ),
                created_at=book.created_at,
                updated_at=book.updated_at,
            )
            self.session.add(model)
        else:
            model.primary_asset_id = book.primary_asset_id.value
            model.created_by_user_id = (
                book.created_by_user_id.value
                if book.created_by_user_id is not None
                else None
            )
            model.title = book.title.value
            model.subtitle = book.subtitle.value if book.subtitle else None
            model.document_type = book.document_type.value
            model.description = book.description.value if book.description else None
            model.language = book.language.value if book.language else None
            model.cover_image_path = (
                book.cover_image_path.value if book.cover_image_path else None
            )
            model.publisher = book.publisher.value if book.publisher else None
            model.published_year = (
                book.published_year.value if book.published_year else None
            )
            model.updated_at = book.updated_at

        if book.created_by_user_id is not None:
            await ensure_library_item(
                self.session,
                user_id=book.created_by_user_id.value,
                book_id=book.id.value,
                created_at=book.created_at,
                updated_at=book.updated_at,
            )

    async def get(self, book_id: BookId) -> Book | None:
        stmt = (
            select(BookModel, BookAssetModel)
            .outerjoin(BookAssetModel, BookAssetModel.id == BookModel.primary_asset_id)
            .where(BookModel.id == book_id.value)
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return None
        model, asset_model = row
        return self._to_entity(model, asset_model)

    async def get_for_owner(
        self, *, book_id: BookId, owner_user_id: UserId
    ) -> Book | None:
        stmt = (
            select(BookModel, BookAssetModel)
            .join(
                LibraryItemModel,
                LibraryItemModel.book_id == BookModel.id,
            )
            .outerjoin(BookAssetModel, BookAssetModel.id == BookModel.primary_asset_id)
            .where(
                BookModel.id == book_id.value,
                LibraryItemModel.user_id == owner_user_id.value,
                LibraryItemModel.access_status == AccessStatus.ACTIVE.value,
            )
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return None
        model, asset_model = row
        return self._to_entity(model, asset_model)

    async def list_for_owner(self, *, owner_user_id: UserId) -> list[Book]:
        stmt = (
            select(BookModel, BookAssetModel)
            .join(
                LibraryItemModel,
                LibraryItemModel.book_id == BookModel.id,
            )
            .outerjoin(BookAssetModel, BookAssetModel.id == BookModel.primary_asset_id)
            .where(
                LibraryItemModel.user_id == owner_user_id.value,
                LibraryItemModel.access_status == AccessStatus.ACTIVE.value,
            )
            .order_by(BookModel.created_at.desc())
        )
        rows = (await self.session.execute(stmt)).all()
        return [self._to_entity(model, asset_model) for model, asset_model in rows]

    async def search(self, *, book_filter: BookFilter) -> list[Book]:
        stmt = (
            select(BookModel, BookAssetModel)
            .join(
                LibraryItemModel,
                LibraryItemModel.book_id == BookModel.id,
            )
            .outerjoin(BookAssetModel, BookAssetModel.id == BookModel.primary_asset_id)
            .where(
                LibraryItemModel.user_id == book_filter.owner_user_id.value,
                LibraryItemModel.access_status == AccessStatus.ACTIVE.value,
            )
        )

        if book_filter.query:
            like = f"%{book_filter.query.strip()}%"
            stmt = stmt.where(
                or_(
                    BookModel.title.ilike(like),
                    BookModel.subtitle.ilike(like),
                    BookModel.description.ilike(like),
                    BookModel.publisher.ilike(like),
                    BookAssetModel.original_filename.ilike(like),
                )
            )

        if book_filter.document_type:
            stmt = stmt.where(BookModel.document_type == book_filter.document_type)
        if book_filter.status:
            stmt = stmt.where(BookAssetModel.processing_status == book_filter.status)
        if book_filter.favorited is True:
            stmt = stmt.where(LibraryItemModel.favorited_at.is_not(None))
        elif book_filter.favorited is False:
            stmt = stmt.where(LibraryItemModel.favorited_at.is_(None))
        if book_filter.archived is True:
            stmt = stmt.where(LibraryItemModel.archived_at.is_not(None))
        elif book_filter.archived is False:
            stmt = stmt.where(LibraryItemModel.archived_at.is_(None))
        if book_filter.completed is True:
            stmt = stmt.where(LibraryItemModel.completed_at.is_not(None))
        elif book_filter.completed is False:
            stmt = stmt.where(LibraryItemModel.completed_at.is_(None))
        if book_filter.continue_reading:
            stmt = stmt.where(
                LibraryItemModel.last_opened_at.is_not(None),
                LibraryItemModel.archived_at.is_(None),
                LibraryItemModel.completed_at.is_(None),
            )

        sort_column = self._sort_column(book_filter.sort_by)
        if book_filter.sort_dir is SortDirection.ASC:
            stmt = stmt.order_by(sort_column.asc().nullslast())
        else:
            stmt = stmt.order_by(sort_column.desc().nullslast())

        rows = (await self.session.execute(stmt)).all()
        return [self._to_entity(model, asset_model) for model, asset_model in rows]

    async def list_by_ids(self, book_ids: list[BookId]) -> list[Book]:
        if not book_ids:
            return []
        raw_ids = [b.value for b in book_ids]
        stmt = (
            select(BookModel, BookAssetModel)
            .outerjoin(BookAssetModel, BookAssetModel.id == BookModel.primary_asset_id)
            .where(BookModel.id.in_(raw_ids))
        )
        rows = (await self.session.execute(stmt)).all()
        return [self._to_entity(model, asset_model) for model, asset_model in rows]

    async def delete(self, *, book_id: BookId) -> None:
        model = await self.session.get(BookModel, book_id.value)
        if model is not None:
            await self.session.delete(model)

    @staticmethod
    def _to_entity(model: BookModel, asset_model: BookAssetModel | None = None) -> Book:
        return Book(
            id=BookId(model.id),
            primary_asset_id=BookAssetId(model.primary_asset_id),
            title=BookTitle(model.title),
            created_by_user_id=(
                UserId(model.created_by_user_id)
                if model.created_by_user_id is not None
                else None
            ),
            subtitle=BookSubtitle(model.subtitle) if model.subtitle else None,
            document_type=BookDocumentType(model.document_type),
            description=(
                BookDescription(model.description) if model.description else None
            ),
            language=BookLanguage(model.language) if model.language else None,
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
            source_filename=(
                BookSourceFilename(asset_model.original_filename)
                if asset_model is not None
                else None
            ),
            file_path=(
                BookFilePath(asset_model.storage_key)
                if asset_model is not None
                else None
            ),
            page_count=(
                BookPageCount(asset_model.page_count)
                if asset_model is not None and asset_model.page_count is not None
                else None
            ),
            word_count=(
                BookWordCount(asset_model.word_count)
                if asset_model is not None and asset_model.word_count is not None
                else None
            ),
            total_chunks=(
                BookTotalChunks(asset_model.total_chunks)
                if asset_model is not None and asset_model.total_chunks is not None
                else None
            ),
            has_images=asset_model.has_images if asset_model is not None else False,
            toc_extracted=(
                asset_model.toc_extracted if asset_model is not None else False
            ),
            status=(
                ProcessingStatus(asset_model.processing_status)
                if asset_model is not None
                else ProcessingStatus.PENDING
            ),
            processing_error=(
                BookProcessingError(asset_model.processing_error)
                if asset_model is not None and asset_model.processing_error
                else None
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _sort_column(sort_by: BookSortField):
        if sort_by is BookSortField.UPDATED_AT:
            return BookModel.updated_at
        if sort_by is BookSortField.TITLE:
            return BookModel.title
        if sort_by is BookSortField.LAST_OPENED_AT:
            return LibraryItemModel.last_opened_at
        return BookModel.created_at
