from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import delete, func, select, text, update

from app.domain.auth.value_objects import UserId
from app.domain.theme.entities import Theme
from app.domain.theme.repositories import ThemeRepository
from app.domain.theme.value_objects import (
    ThemeDescription,
    ThemeId,
    ThemeName,
    ThemeSlug,
    ThemeTokens,
)
from app.infrastructure.persistence.models.theme import (
    ThemeLikeModel,
    ThemeModel,
    UserActiveThemeModel,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SqlAlchemyThemeRepository(ThemeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save(self, theme: Theme) -> None:
        model = await self.session.get(ThemeModel, theme.id.value)

        if model is None:
            model = ThemeModel(
                id=theme.id.value,
                owner_user_id=theme.owner_user_id.value
                if theme.owner_user_id
                else None,
                name=theme.name.value,
                slug=theme.slug.value,
                description=theme.description.value if theme.description else None,
                tokens=theme.tokens.value,
                preview_image_url=theme.preview_image_url,
                tags=theme.tags,
                is_public=theme.is_public,
                is_system=theme.is_system,
                is_featured=theme.is_featured,
                download_count=theme.download_count,
                like_count=theme.like_count,
                forked_from_id=theme.forked_from_id.value
                if theme.forked_from_id
                else None,
                created_at=theme.created_at,
                updated_at=theme.updated_at,
            )
            self.session.add(model)
            return

        model.name = theme.name.value
        model.slug = theme.slug.value  # type: ignore[assignment]
        model.description = theme.description.value if theme.description else None
        model.tokens = theme.tokens.value
        model.preview_image_url = theme.preview_image_url
        model.tags = theme.tags
        model.is_public = theme.is_public
        model.is_featured = theme.is_featured
        model.updated_at = theme.updated_at

    async def get(self, theme_id: ThemeId) -> Theme | None:
        model = await self.session.get(ThemeModel, theme_id.value)
        if model is None:
            return None
        return self._to_entity(model)

    async def get_by_slug(self, *, slug: ThemeSlug) -> Theme | None:
        stmt = select(ThemeModel).where(ThemeModel.slug == slug.value)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def get_for_owner(
        self, *, theme_id: ThemeId, user_id: UserId
    ) -> Theme | None:
        stmt = select(ThemeModel).where(
            ThemeModel.id == theme_id.value,
            ThemeModel.owner_user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_for_user(self, *, user_id: UserId) -> list[Theme]:
        stmt = (
            select(ThemeModel)
            .where(ThemeModel.owner_user_id == user_id.value)
            .order_by(ThemeModel.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_public(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
        sort_by: str = "popular",
        query: str | None = None,
    ) -> tuple[list[Theme], int]:
        base = select(ThemeModel).where(ThemeModel.is_public.is_(True))

        if query:
            base = base.where(
                ThemeModel.search_vector.op("@@")(
                    func.plainto_tsquery("english", query)
                )
            )

        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        if sort_by == "new":
            base = base.order_by(ThemeModel.created_at.desc())
        elif sort_by == "featured":
            base = base.order_by(
                ThemeModel.is_featured.desc(),
                ThemeModel.download_count.desc(),
            )
        else:  # popular
            base = base.order_by(ThemeModel.download_count.desc())

        offset = (page - 1) * per_page
        stmt = base.offset(offset).limit(per_page)
        result = await self.session.execute(stmt)
        themes = [self._to_entity(m) for m in result.scalars().all()]
        return themes, total

    async def delete(self, theme_id: ThemeId) -> None:
        stmt = delete(ThemeModel).where(ThemeModel.id == theme_id.value)
        await self.session.execute(stmt)

    # ── User active theme ──

    async def get_active_theme_id(self, *, user_id: UserId) -> ThemeId | None:
        stmt = select(UserActiveThemeModel.theme_id).where(
            UserActiveThemeModel.user_id == user_id.value,
        )
        result = await self.session.execute(stmt)
        theme_id = result.scalar_one_or_none()
        if theme_id is None:
            return None
        return ThemeId(theme_id)

    async def set_active_theme(self, *, user_id: UserId, theme_id: ThemeId) -> None:
        await self.session.execute(
            text(
                "INSERT INTO user_active_themes (user_id, theme_id, updated_at) "
                "VALUES (:user_id, :theme_id, now()) "
                "ON CONFLICT (user_id) DO UPDATE SET theme_id = :theme_id, updated_at = now()"
            ).bindparams(
                user_id=user_id.value,
                theme_id=theme_id.value,
            )
        )

    # ── Likes ──

    async def has_user_liked(self, *, user_id: UserId, theme_id: ThemeId) -> bool:
        stmt = select(ThemeLikeModel).where(
            ThemeLikeModel.user_id == user_id.value,
            ThemeLikeModel.theme_id == theme_id.value,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def add_like(self, *, user_id: UserId, theme_id: ThemeId) -> None:
        model = ThemeLikeModel(
            user_id=user_id.value,
            theme_id=theme_id.value,
        )
        self.session.add(model)
        # Atomic increment
        await self.session.execute(
            update(ThemeModel)
            .where(ThemeModel.id == theme_id.value)
            .values(like_count=ThemeModel.like_count + 1)
        )

    async def remove_like(self, *, user_id: UserId, theme_id: ThemeId) -> None:
        stmt = delete(ThemeLikeModel).where(
            ThemeLikeModel.user_id == user_id.value,
            ThemeLikeModel.theme_id == theme_id.value,
        )
        await self.session.execute(stmt)
        # Atomic decrement
        await self.session.execute(
            update(ThemeModel)
            .where(ThemeModel.id == theme_id.value, ThemeModel.like_count > 0)
            .values(like_count=ThemeModel.like_count - 1)
        )

    # ── Mapping ──

    @staticmethod
    def _to_entity(model: ThemeModel) -> Theme:
        if model.slug is None:
            raise ValueError(f"Theme {model.id} is missing a slug.")

        return Theme(
            id=ThemeId(model.id),
            name=ThemeName(model.name),
            slug=ThemeSlug(model.slug),
            tokens=ThemeTokens(model.tokens),
            owner_user_id=UserId(model.owner_user_id) if model.owner_user_id else None,
            description=ThemeDescription(model.description)
            if model.description
            else None,
            preview_image_url=model.preview_image_url,
            tags=model.tags,
            is_public=model.is_public,
            is_system=model.is_system,
            is_featured=model.is_featured,
            download_count=model.download_count,
            like_count=model.like_count,
            forked_from_id=ThemeId(model.forked_from_id)
            if model.forked_from_id
            else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
