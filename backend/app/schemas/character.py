"""
角色相关的Pydantic模式

用于API请求和响应的数据验证
"""

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from app.models.character import (
    CharacterTagPublic,
)


# 角色基础模式
class CharacterBase(SQLModel):
    name: str = Field(max_length=100, description="角色名称")
    short_bio: Optional[str] = Field(
        default=None, max_length=500, description="角色简介"
    )
    avatar_url: Optional[str] = Field(
        default=None, max_length=500, description="头像URL"
    )
    persona_text: Optional[str] = Field(default=None, description="角色人格定义")
    example_lines: Optional[List[str]] = Field(default=None, description="示例台词")
    source: Optional[str] = Field(default=None, max_length=200, description="来源/版权")
    is_active: bool = Field(default=True, description="是否激活")
    default_voice: Optional[str] = Field(
        default="Cherry", max_length=50, description="默认音色"
    )


# 角色创建模式
class CharacterCreate(CharacterBase):
    tag_ids: Optional[List[uuid.UUID]] = Field(default=None, description="标签ID列表")


# 角色更新模式
class CharacterUpdate(SQLModel):
    name: Optional[str] = Field(default=None, max_length=100)
    short_bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    persona_text: Optional[str] = Field(default=None)
    example_lines: Optional[List[str]] = Field(default=None)
    source: Optional[str] = Field(default=None, max_length=200)
    is_active: Optional[bool] = Field(default=None)
    default_voice: Optional[str] = Field(default=None, max_length=50)
    tag_ids: Optional[List[uuid.UUID]] = Field(default=None)


# 角色公开模式（API响应）
class CharacterPublic(CharacterBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    tags: List[CharacterTagPublic] = Field(default_factory=list)


# 角色列表响应模式
class CharactersPublic(SQLModel):
    data: List[CharacterPublic]
    count: int


# 角色搜索请求模式
class CharacterSearchRequest(SQLModel):
    query: str = Field(description="搜索关键词")
    search_type: str = Field(
        default="text", description="搜索类型: text, vector, hybrid"
    )
    limit: int = Field(default=10, ge=1, le=100, description="返回数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")
    tag_ids: Optional[List[uuid.UUID]] = Field(default=None, description="标签过滤")
    is_active: Optional[bool] = Field(default=True, description="是否只返回激活的角色")


# 角色搜索结果模式
class CharacterSearchResult(SQLModel):
    character: CharacterPublic
    score: Optional[float] = Field(default=None, description="相似度分数")
    match_type: str = Field(description="匹配类型")


# 角色搜索响应模式
class CharacterSearchResponse(SQLModel):
    results: List[CharacterSearchResult]
    total: int
    query: str
    search_type: str


# 嵌入模型信息模式
class EmbeddingModelInfo(SQLModel):
    provider: str = Field(description="提供商")
    model_name: str = Field(description="模型名称")
    dimension: int = Field(description="向量维度")


# 嵌入模型切换请求模式
class EmbeddingProviderSwitch(SQLModel):
    provider: str = Field(description="提供商: openai, aliyun")


# 批量操作请求模式
class CharacterBatchRequest(SQLModel):
    character_ids: List[uuid.UUID] = Field(description="角色ID列表")
    action: str = Field(description="操作类型: activate, deactivate, delete")


# 批量操作响应模式
class CharacterBatchResponse(SQLModel):
    success_count: int = Field(description="成功数量")
    failed_count: int = Field(description="失败数量")
    failed_ids: List[uuid.UUID] = Field(
        default_factory=list, description="失败的角色ID"
    )
    message: str = Field(description="操作结果消息")


# 角色生成请求模式
class CharacterGenerateRequest(BaseModel):
    """角色生成请求"""

    name: str = Field(..., max_length=100, description="角色名称")
    character_type: str = Field(
        ..., max_length=50, description="角色类型，如：动漫角色、历史人物、原创角色等"
    )
    background: Optional[str] = Field(
        default=None, max_length=1000, description="背景描述"
    )


# 角色生成响应模式
class CharacterGenerateResponse(BaseModel):
    """角色生成响应"""

    name: str = Field(..., description="角色名称")
    short_bio: str = Field(..., description="角色简介")
    persona_text: str = Field(..., description="详细人格设定")
    example_lines: List[str] = Field(..., description="示例对话")
    suggested_voice: str = Field(..., description="推荐音色")