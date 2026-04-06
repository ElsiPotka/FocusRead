from uuid import UUID  # noqa: TC003

from pydantic import BaseModel, EmailStr, Field

from app.domain.auth.entities import User  # noqa: TC001


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    surname: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str | None = Field(None, description="Required for mobile clients")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    name: str
    surname: str
    email: str
    email_verified: bool
    image: str | None
    full_name: str
    is_active: bool

    @staticmethod
    def from_entity(user: User) -> UserResponse:
        return UserResponse(
            id=user.id.value,
            name=user.name,
            surname=user.surname,
            email=user.email.value,
            email_verified=user.email_verified,
            image=user.image,
            full_name=user.full_name,
            is_active=user.is_active,
        )


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse
