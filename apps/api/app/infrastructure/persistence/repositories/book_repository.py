from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import and_, exists, func, literal, or_, select

from app.domain.auth.value_objects import UserId
from app.domain.books.entities import Book, BookStatus
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
from app.infrastructure.persistence.models.book import BookModel
from app.infrastructure.persistence.models.contributor import (
    BookContributorModel,
    ContributorModel,
)
from app.infrastructure.persistence.models.label import BookLabelModel, LabelModel
from app.infrastructure.persistence.models.shelf import ShelfBookModel, ShelfModel
from app.infrastructure.persistence.models.user_book_state import UserBookStateModel

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

    async def search(self, *, book_filter: BookFilter) -> list[Book]:
        stmt = select(BookModel)
        conditions: list = [
            BookModel.owner_user_id == book_filter.owner_user_id.value,
        ]

        if book_filter.query:
            tsquery = func.plainto_tsquery("english", book_filter.query)

            book_match = BookModel.search_vector.op("@@")(tsquery)

            contributor_match = exists(
                select(literal(1))
                .select_from(BookContributorModel)
                .join(ContributorModel)
                .where(
                    BookContributorModel.book_id == BookModel.id,
                    ContributorModel.search_vector.op("@@")(tsquery),
                )
            )

            shelf_match = exists(
                select(literal(1))
                .select_from(ShelfBookModel)
                .join(ShelfModel)
                .where(
                    ShelfBookModel.book_id == BookModel.id,
                    ShelfModel.user_id == book_filter.owner_user_id.value,
                    ShelfModel.search_vector.op("@@")(tsquery),
                )
            )

            label_match = exists(
                select(literal(1))
                .select_from(BookLabelModel)
                .join(LabelModel)
                .where(
                    BookLabelModel.book_id == BookModel.id,
                    or_(
                        LabelModel.owner_user_id == book_filter.owner_user_id.value,
                        LabelModel.is_system.is_(True),
                    ),
                    LabelModel.search_vector.op("@@")(tsquery),
                )
            )

            conditions.append(
                or_(book_match, contributor_match, shelf_match, label_match)
            )

        needs_state_join = any([
            book_filter.favorited is not None,
            book_filter.archived is not None,
            book_filter.completed is not None,
            book_filter.continue_reading is not None,
            book_filter.sort_by == BookSortField.LAST_OPENED_AT,
        ])

        if needs_state_join:
            stmt = stmt.outerjoin(
                UserBookStateModel,
                and_(
                    UserBookStateModel.book_id == BookModel.id,
                    UserBookStateModel.user_id == book_filter.owner_user_id.value,
                ),
            )

        no_state_row = UserBookStateModel.user_id.is_(None)

        if book_filter.favorited is True:
            conditions.append(UserBookStateModel.favorited_at.is_not(None))
        elif book_filter.favorited is False:
            conditions.append(
                or_(UserBookStateModel.favorited_at.is_(None), no_state_row)
            )

        if book_filter.archived is True:
            conditions.append(UserBookStateModel.archived_at.is_not(None))
        elif book_filter.archived is False:
            conditions.append(
                or_(UserBookStateModel.archived_at.is_(None), no_state_row)
            )

        if book_filter.completed is True:
            conditions.append(UserBookStateModel.completed_at.is_not(None))
        elif book_filter.completed is False:
            conditions.append(
                or_(UserBookStateModel.completed_at.is_(None), no_state_row)
            )

        if book_filter.continue_reading is True:
            conditions.append(UserBookStateModel.last_opened_at.is_not(None))
            conditions.append(
                or_(UserBookStateModel.completed_at.is_(None), no_state_row)
            )

        if book_filter.document_type:
            conditions.append(BookModel.document_type == book_filter.document_type)
        if book_filter.status:
            conditions.append(BookModel.status == book_filter.status)

        stmt = stmt.where(*conditions)

        sort_col_map = {
            BookSortField.CREATED_AT: BookModel.created_at,
            BookSortField.TITLE: BookModel.title,
            BookSortField.LAST_OPENED_AT: UserBookStateModel.last_opened_at,
        }
        sort_col = sort_col_map[book_filter.sort_by]

        if book_filter.sort_dir == SortDirection.DESC:
            stmt = stmt.order_by(sort_col.desc().nullslast())
        else:
            stmt = stmt.order_by(sort_col.asc().nullsfirst())

        if book_filter.limit is not None:
            stmt = stmt.limit(book_filter.limit)
        if book_filter.offset:
            stmt = stmt.offset(book_filter.offset)

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
