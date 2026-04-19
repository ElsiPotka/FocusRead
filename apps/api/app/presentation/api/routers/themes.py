from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID  # noqa: TC003

from fastapi import APIRouter, Depends, Query, Security

from app.application.themes import (
    ApplyTheme,
    BrowseMarketplace,
    CreateTheme,
    DeleteTheme,
    FeatureTheme,
    ForkTheme,
    GetActiveTheme,
    GetTheme,
    LikeTheme,
    ListUserThemes,
    PublishTheme,
    UnfeatureTheme,
    UnpublishTheme,
    UpdateTheme,
)
from app.domain.role.value_objects import RoleName
from app.infrastructure.cache.redis import get_cache
from app.infrastructure.persistence.unit_of_work import get_uow
from app.presentation.api.middleware.auth import get_current_user, role_guard
from app.presentation.api.schemas.pagination import PaginatedResponse, PaginationMeta
from app.presentation.api.schemas.response import (
    APIResponse,
    ListResponse,
    MessageResponse,
)
from app.presentation.api.schemas.themes import (
    ApplyThemeRequest,
    CreateThemeRequest,
    ThemeDetailResponse,
    ThemeResponse,
    ThemeTokensResponse,
    UpdateThemeRequest,
)

if TYPE_CHECKING:
    from app.domain.auth.entities import User
    from app.infrastructure.cache.redis_cache import RedisCache

router = APIRouter(prefix="/themes", tags=["themes"])


# ── User active theme (must be before /{theme_id}) ──


@router.get("/me/active")
async def get_active_theme(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[ThemeTokensResponse]:
    use_case = GetActiveTheme(uow, cache)
    tokens = await use_case.execute(user_id=current_user.id.value)
    return APIResponse(
        success=True,
        data=ThemeTokensResponse(tokens=tokens),
        message="Active theme retrieved",
    )


@router.post("/me/active")
async def apply_theme(
    body: ApplyThemeRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> MessageResponse:
    use_case = ApplyTheme(uow, cache)
    await use_case.execute(
        user_id=current_user.id.value,
        theme_id=body.theme_id,
    )
    return MessageResponse(success=True, message="Theme applied")


@router.get("/me")
async def list_my_themes(
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> ListResponse[ThemeResponse]:
    use_case = ListUserThemes(uow)
    themes = await use_case.execute(user_id=current_user.id.value)
    return ListResponse(
        success=True,
        data=[ThemeResponse.from_entity(t) for t in themes],
        count=len(themes),
        message="Themes retrieved",
    )


# ── Marketplace ──


@router.get("/marketplace")
async def browse_marketplace(
    q: str | None = Query(None, description="Search query"),
    sort_by: str = Query("popular", description="Sort: popular, new, featured"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    uow=Depends(get_uow),
) -> PaginatedResponse[ThemeResponse]:
    use_case = BrowseMarketplace(uow)
    themes, total = await use_case.execute(
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        query=q,
    )
    total_pages = (total + per_page - 1) // per_page
    return PaginatedResponse(
        items=[ThemeResponse.from_entity(t) for t in themes],
        meta=PaginationMeta(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            next_cursor=None,
            prev_cursor=None,
        ),
    )


# ── CRUD ──


@router.post("")
async def create_theme(
    body: CreateThemeRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ThemeDetailResponse]:
    use_case = CreateTheme(uow)
    theme = await use_case.execute(
        user_id=current_user.id.value,
        name=body.name,
        tokens=body.tokens,
        description=body.description,
        tags=body.tags,
    )
    return APIResponse(
        success=True,
        data=ThemeDetailResponse.from_entity(theme),
        message="Theme created",
    )


@router.get("/{theme_id}")
async def get_theme(
    theme_id: UUID,
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[ThemeDetailResponse]:
    use_case = GetTheme(uow, cache)
    theme = await use_case.execute(theme_id=theme_id)
    return APIResponse(
        success=True,
        data=ThemeDetailResponse.from_entity(theme),
        message="Theme retrieved",
    )


@router.patch("/{theme_id}")
async def update_theme(
    theme_id: UUID,
    body: UpdateThemeRequest,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> APIResponse[ThemeDetailResponse]:
    use_case = UpdateTheme(uow, cache)
    theme = await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
        name=body.name,
        description=body.description,
        tokens=body.tokens,
        tags=body.tags,
    )
    return APIResponse(
        success=True,
        data=ThemeDetailResponse.from_entity(theme),
        message="Theme updated",
    )


@router.delete("/{theme_id}")
async def delete_theme(
    theme_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> MessageResponse:
    use_case = DeleteTheme(uow, cache)
    await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Theme deleted")


# ── Actions ──


@router.post("/{theme_id}/fork")
async def fork_theme(
    theme_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> APIResponse[ThemeDetailResponse]:
    use_case = ForkTheme(uow)
    theme = await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
    )
    return APIResponse(
        success=True,
        data=ThemeDetailResponse.from_entity(theme),
        message="Theme forked",
    )


@router.post("/{theme_id}/publish")
async def publish_theme(
    theme_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = PublishTheme(uow)
    await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Theme published")


@router.post("/{theme_id}/unpublish")
async def unpublish_theme(
    theme_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = UnpublishTheme(uow)
    await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
    )
    return MessageResponse(success=True, message="Theme unpublished")


@router.post("/{theme_id}/like")
async def like_theme(
    theme_id: UUID,
    current_user: User = Security(get_current_user, scopes=["me"]),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = LikeTheme(uow)
    liked = await use_case.execute(
        theme_id=theme_id,
        user_id=current_user.id.value,
    )
    msg = "Theme liked" if liked else "Theme unliked"
    return MessageResponse(success=True, message=msg)


# ── Admin ──


@router.post("/{theme_id}/feature")
async def feature_theme(
    theme_id: UUID,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = FeatureTheme(uow)
    await use_case.execute(theme_id=theme_id)
    return MessageResponse(success=True, message="Theme featured")


@router.post("/{theme_id}/unfeature")
async def unfeature_theme(
    theme_id: UUID,
    _current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
) -> MessageResponse:
    use_case = UnfeatureTheme(uow)
    await use_case.execute(theme_id=theme_id)
    return MessageResponse(success=True, message="Theme unfeatured")


@router.delete("/{theme_id}/admin")
async def admin_delete_theme(
    theme_id: UUID,
    current_admin: User = Depends(role_guard(RoleName.ADMIN)),
    uow=Depends(get_uow),
    cache: RedisCache = Depends(get_cache),
) -> MessageResponse:
    use_case = DeleteTheme(uow, cache)
    await use_case.execute(
        theme_id=theme_id,
        user_id=current_admin.id.value,
        is_admin=True,
    )
    return MessageResponse(success=True, message="Theme deleted by admin")
