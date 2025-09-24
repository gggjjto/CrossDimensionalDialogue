"""
音色目录相关的Pydantic模式
"""

import uuid
from typing import List, Optional
from pydantic import BaseModel, Field


class VoiceCatalogResponse(BaseModel):
    """音色目录响应模式"""

    id: uuid.UUID
    provider: str
    name: str
    voice: str
    preview_url: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str


class VoiceCatalogListResponse(BaseModel):
    """音色目录列表响应模式"""

    items: List[VoiceCatalogResponse]
    total: int
    skip: int
    limit: int


class VoiceCatalogQueryParams(BaseModel):
    """音色目录查询参数"""

    provider: Optional[str] = Field(None, description="提供方过滤")
    is_active: Optional[bool] = Field(None, description="是否可用过滤")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=1000, description="限制数量")


class VoiceCatalogSearchRequest(BaseModel):
    """音色目录搜索请求"""

    query: Optional[str] = Field(None, description="搜索关键词")
    provider: Optional[str] = Field(None, description="提供方过滤")
    is_active: Optional[bool] = Field(None, description="是否可用过滤")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=1000, description="限制数量")
