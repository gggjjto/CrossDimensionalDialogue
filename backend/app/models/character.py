import uuid
from datetime import datetime
from typing import List, Optional

from sqlmodel import Relationship, SQLModel, Field, JSON
from pgvector.sqlalchemy import Vector


# 标签表
class CharacterTagBase(SQLModel):
    name: str = Field(max_length=50, unique=True, index=True, description="标签名称")
    description: Optional[str] = Field(
        default=None, max_length=255, description="标签描述"
    )
    color: Optional[str] = Field(
        default=None, max_length=7, description="标签颜色（十六进制）"
    )


class CharacterTagCreate(CharacterTagBase):
    pass


class CharacterTagUpdate(CharacterTagBase):
    name: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    color: Optional[str] = Field(default=None, max_length=7)


class CharacterTag(CharacterTagBase, table=True):
    __tablename__ = "character_tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    character_relations: List["CharacterTagMap"] = Relationship(back_populates="tag")


class CharacterTagPublic(CharacterTagBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CharacterTagsPublic(SQLModel):
    data: List[CharacterTagPublic]
    count: int


# 角色基本信息
class CharacterBase(SQLModel):
    name: str = Field(max_length=100, index=True, description="角色名称")
    short_bio: str = Field(max_length=500, description="角色简介")
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description="头像URL"
    )
    persona_text: str = Field(description="角色人格定义（系统prompt）")
    example_lines: Optional[List[str]] = Field(
        default=None, sa_type=JSON, description="示例台词列表"
    )
    source: Optional[str] = Field(
        default=None, max_length=200, description="来源/版权声明"
    )
    is_active: bool = Field(default=True, description="是否可用")


class CharacterCreate(CharacterBase):
    example_lines: Optional[List[str]] = Field(
        default=None, sa_type=JSON, description="示例台词列表"
    )
    tag_ids: Optional[List[uuid.UUID]] = Field(
        default=None, description="关联的标签ID列表"
    )


class CharacterUpdate(CharacterBase):
    name: Optional[str] = Field(default=None, max_length=100)
    short_bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    persona_text: Optional[str] = Field(default=None)
    example_lines: Optional[List[str]] = Field(default=None)
    source: Optional[str] = Field(default=None, max_length=200)
    is_active: Optional[bool] = Field(default=None)
    tag_ids: Optional[List[uuid.UUID]] = Field(
        default=None, description="关联的标签ID列表"
    )


class Character(CharacterBase, table=True):
    __tablename__ = "characters"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    tag_relations: List["CharacterTagMap"] = Relationship(
        back_populates="character", cascade_delete=True
    )
    embeddings: List["CharacterEmbedding"] = Relationship(
        back_populates="character", cascade_delete=True
    )


class CharacterPublic(CharacterBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tags: Optional[List[CharacterTagPublic]] = Field(
        default=None, description="关联的标签"
    )


class CharactersPublic(SQLModel):
    data: List[CharacterPublic]
    count: int


# 角色-标签关系表
class CharacterTagMapBase(SQLModel):
    character_id: uuid.UUID = Field(foreign_key="characters.id", description="角色ID")
    tag_id: uuid.UUID = Field(foreign_key="character_tags.id", description="标签ID")


class CharacterTagMap(CharacterTagMapBase, table=True):
    __tablename__ = "character_tag_maps"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    character: Optional[Character] = Relationship(back_populates="tag_relations")
    tag: Optional[CharacterTag] = Relationship(back_populates="character_relations")


# 角色向量表（用于搜索/RAG）
class CharacterEmbeddingBase(SQLModel):
    character_id: uuid.UUID = Field(foreign_key="characters.id", description="角色ID")
    embedding_type: str = Field(
        max_length=50, description="向量类型（persona/knowledge）"
    )
    model_name: str = Field(max_length=100, description="使用的embedding模型名称")
    dimension: int = Field(description="向量维度")


class CharacterEmbeddingCreate(CharacterEmbeddingBase):
    embedding: List[float] = Field(description="向量数据")


class CharacterEmbedding(CharacterEmbeddingBase, table=True):
    __tablename__ = "character_embeddings"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    embedding: List[float] = Field(sa_type=Vector, description="向量数据")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 关系
    character: Optional[Character] = Relationship(back_populates="embeddings")


class CharacterEmbeddingPublic(CharacterEmbeddingBase):
    id: uuid.UUID
    created_at: datetime


# 角色搜索相关模型
class CharacterSearchRequest(SQLModel):
    query: str = Field(description="搜索查询")
    search_type: str = Field(default="text", description="搜索类型：text/vector/hybrid")
    limit: int = Field(default=10, ge=1, le=100, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")
    tag_ids: Optional[List[uuid.UUID]] = Field(default=None, description="标签过滤")
    is_active: Optional[bool] = Field(default=True, description="是否只搜索可用角色")


class CharacterSearchResult(SQLModel):
    character: CharacterPublic
    score: Optional[float] = Field(
        default=None, description="相似度分数（向量搜索时使用）"
    )
    match_type: str = Field(description="匹配类型：text/vector/hybrid")


class CharacterSearchResponse(SQLModel):
    results: List[CharacterSearchResult]
    total: int
    query: str
    search_type: str
