from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class VoiceCatalogBase(SQLModel):
    """音色目录基础模型（用于管理可用的合成音色元数据）。"""

    provider: str = Field(
        default="qwen3-tts",
        description="提供方/模型家族标识，例如 qwen3-tts",
        max_length=50,
    )
    name: str = Field(..., description="音色名（展示名）", max_length=100)
    voice: str = Field(..., description="调用时的 voice 参数", max_length=100)
    preview_url: Optional[str] = Field(
        None, description="音色效果预览URL（可选）", max_length=500
    )
    description: Optional[str] = Field(None, description="音色描述", max_length=500)
    is_active: bool = Field(default=True, description="是否可用")


class VoiceCatalog(VoiceCatalogBase, table=True):
    """音色目录表。"""

    __tablename__ = "voice_catalog"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class VoiceCatalogCreate(VoiceCatalogBase):
    """创建音色目录项。"""

    pass


class VoiceCatalogUpdate(SQLModel):
    """更新音色目录项。"""

    name: Optional[str] = Field(None, max_length=100)
    voice: Optional[str] = Field(None, max_length=100)
    preview_url: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None


class VoiceCatalogPublic(VoiceCatalogBase):
    """对外公开的音色目录项。"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
