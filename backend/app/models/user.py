import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.conversation import Conversation
    from app.models.character import Character


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(
        default=None, max_length=500, description="用户头像URL"
    )
    bio: str | None = Field(default=None, max_length=1000, description="个人简介")
    location: str | None = Field(default=None, max_length=100, description="所在地")
    website: str | None = Field(default=None, max_length=500, description="个人网站")


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(
        default=None, max_length=500, description="用户头像URL"
    )
    bio: str | None = Field(default=None, max_length=1000, description="个人简介")
    location: str | None = Field(default=None, max_length=100, description="所在地")
    website: str | None = Field(default=None, max_length=500, description="个人网站")


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    avatar_url: str | None = Field(
        default=None, max_length=500, description="用户头像URL"
    )
    bio: str | None = Field(default=None, max_length=1000, description="个人简介")
    location: str | None = Field(default=None, max_length=100, description="所在地")
    website: str | None = Field(default=None, max_length=500, description="个人网站")


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="注册时间"
    )
    character_count: int = Field(default=0, description="创建智能体数量")
    conversation_count: int = Field(default=0, description="对话次数")
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    conversations: List["Conversation"] = Relationship(
        back_populates="user", cascade_delete=True
    )
    characters: List["Character"] = Relationship(
        back_populates="user", cascade_delete=True
    )


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime
    character_count: int
    conversation_count: int


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int
