"""
对话编排相关的Pydantic模型
"""

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.conversation import ConversationSettings, LLMProvider


class SendMessageRequest(BaseModel):
    """发送消息请求模型"""

    message: str = Field(..., min_length=1, max_length=2000, description="用户消息内容")
    settings: Optional[ConversationSettings] = Field(
        default=None, description="会话设置"
    )


class SendMessageResponse(BaseModel):
    """发送消息响应模型"""

    success: bool = Field(..., description="是否成功")
    user_message_id: Optional[uuid.UUID] = Field(default=None, description="用户消息ID")
    character_message_id: Optional[uuid.UUID] = Field(
        default=None, description="角色消息ID"
    )
    character_response: Optional[str] = Field(default=None, description="角色回复内容")
    audio_url: Optional[str] = Field(default=None, description="语音回复URL")
    usage: Optional[Dict[str, int]] = Field(default=None, description="Token使用情况")
    error: Optional[str] = Field(default=None, description="错误信息")


class ConversationContextResponse(BaseModel):
    """会话上下文响应模型"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")
    character_name: str = Field(..., description="角色名称")
    character_bio: Optional[str] = Field(default=None, description="角色简介")
    recent_messages: List[Dict[str, Any]] = Field(default=[], description="最近消息")
    message_count: int = Field(default=0, description="消息数量")
    context_window_size: int = Field(default=10, description="上下文窗口大小")


class MessageInfo(BaseModel):
    """消息信息模型"""

    id: uuid.UUID = Field(..., description="消息ID")
    content: str = Field(..., description="消息内容")
    sender_type: str = Field(..., description="发送者类型")
    sender_name: Optional[str] = Field(default=None, description="发送者名称")
    created_at: datetime = Field(..., description="创建时间")


class UpdateConversationSettingsRequest(BaseModel):
    """更新会话设置请求模型"""

    temperature: Optional[float] = Field(
        default=None, ge=0.0, le=2.0, description="温度参数"
    )
    max_tokens: Optional[int] = Field(
        default=None, ge=1, le=4000, description="最大token数"
    )
    top_p: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="top_p参数"
    )
    context_window_size: Optional[int] = Field(
        default=None, ge=1, le=50, description="上下文窗口大小"
    )
    enable_context_summary: Optional[bool] = Field(
        default=None, description="是否启用上下文摘要"
    )
    enable_tts: Optional[bool] = Field(default=None, description="是否启用TTS")
    tts_voice: Optional[str] = Field(default=None, description="TTS音色")
    auto_save: Optional[bool] = Field(default=None, description="是否自动保存")
    enable_typing_indicator: Optional[bool] = Field(
        default=None, description="是否显示输入状态"
    )


class ConversationSettingsResponse(BaseModel):
    """会话设置响应模型"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")
    settings: ConversationSettings = Field(..., description="会话设置")
    updated_at: datetime = Field(..., description="更新时间")
