"""
知识库相关模型
"""

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlmodel import SQLModel, Field, JSON


class KnowledgeType(str, Enum):
    """知识类型枚举"""

    TEXT = "text"  # 文本知识
    DOCUMENT = "document"  # 文档知识
    FAQ = "faq"  # 常见问题
    CHARACTER_BACKGROUND = "character_background"  # 角色背景
    WORLD_BUILDING = "world_building"  # 世界观设定


class KnowledgeSource(str, Enum):
    """知识来源枚举"""

    MANUAL = "manual"  # 手动添加
    UPLOAD = "upload"  # 文件上传
    WEB_SCRAPING = "web_scraping"  # 网页抓取
    API_IMPORT = "api_import"  # API导入
    AI_GENERATED = "ai_generated"  # AI生成


class KnowledgeBase(SQLModel, table=True):
    """知识库模型"""

    __tablename__ = "knowledge_bases"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    character_id: Optional[uuid.UUID] = Field(
        foreign_key="characters.id", description="关联角色ID"
    )
    knowledge_type: KnowledgeType = Field(
        default=KnowledgeType.TEXT, description="知识类型"
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.MANUAL, description="知识来源"
    )
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeItem(SQLModel, table=True):
    """知识条目模型"""

    __tablename__ = "knowledge_items"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    knowledge_base_id: uuid.UUID = Field(
        foreign_key="knowledge_bases.id", description="知识库ID"
    )
    title: str = Field(max_length=500, description="知识标题")
    content: str = Field(description="知识内容")
    summary: Optional[str] = Field(default=None, description="知识摘要")
    tags: Optional[List[str]] = Field(default=None, sa_type=JSON, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, sa_type=JSON, description="元数据"
    )
    embedding: Optional[List[float]] = Field(
        default=None, sa_type=JSON, description="向量嵌入"
    )
    relevance_score: Optional[float] = Field(default=None, description="相关性分数")
    access_count: int = Field(default=0, description="访问次数")
    is_active: bool = Field(default=True, description="是否激活")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class KnowledgeBaseCreate(SQLModel):
    """创建知识库模型"""

    name: str = Field(max_length=255, description="知识库名称")
    description: Optional[str] = Field(default=None, description="知识库描述")
    character_id: Optional[uuid.UUID] = Field(default=None, description="关联角色ID")
    knowledge_type: KnowledgeType = Field(
        default=KnowledgeType.TEXT, description="知识类型"
    )
    source: KnowledgeSource = Field(
        default=KnowledgeSource.MANUAL, description="知识来源"
    )


class KnowledgeItemCreate(SQLModel):
    """创建知识条目模型"""

    knowledge_base_id: uuid.UUID = Field(description="知识库ID")
    title: str = Field(max_length=500, description="知识标题")
    content: str = Field(description="知识内容")
    summary: Optional[str] = Field(default=None, description="知识摘要")
    tags: Optional[List[str]] = Field(default=None, description="标签")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class KnowledgeSearchRequest(SQLModel):
    """知识搜索请求模型"""

    query: str = Field(description="搜索查询")
    knowledge_base_ids: Optional[List[uuid.UUID]] = Field(
        default=None, description="知识库ID列表"
    )
    character_id: Optional[uuid.UUID] = Field(default=None, description="角色ID")
    knowledge_types: Optional[List[KnowledgeType]] = Field(
        default=None, description="知识类型列表"
    )
    max_results: int = Field(default=5, ge=1, le=20, description="最大结果数")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="相关性阈值")


class KnowledgeSearchResult(SQLModel):
    """知识搜索结果模型"""

    knowledge_item: KnowledgeItem
    relevance_score: float = Field(description="相关性分数")
    matched_content: Optional[str] = Field(default=None, description="匹配的内容片段")
    context: Optional[str] = Field(default=None, description="上下文信息")
