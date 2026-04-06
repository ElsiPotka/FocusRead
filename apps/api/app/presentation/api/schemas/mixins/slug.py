import re

from pydantic import BaseModel, Field, field_validator

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class SlugMixin(BaseModel):
    slug: str | None = Field(
        default=None,
        description="URL-friendly identifier",
        examples=["my-awesome-book"],
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip().lower().replace("_", "-")
        if len(v) > 255:
            raise ValueError("Slug is too long")
        if not SLUG_RE.fullmatch(v):
            raise ValueError(
                "Slug must contain only lowercase letters, numbers, and hyphens"
            )
        return v
