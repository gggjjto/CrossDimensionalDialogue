import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.conversation import (
    ContentType,
    ContextType,
    ConversationStatus,
    MessageStatus,
    SenderType,
)
from app.schemas.character import CharacterPublic
from app.schemas.user import UserPublic
from pydantic import BaseModel, Field, field_validator
from sqlmodel import SQLModel


# 会话相关模式
class ConversationBase(SQLModel):
    """会话基础模式"""

    title: str = Field(..., max_length=255, description="会话标题")
    description: Optional[str] = Field(None, description="会话描述")
    status: ConversationStatus = Field(
        ConversationStatus.ACTIVE, description="会话状态"
    )
    settings: Optional[Dict[str, Any]] = Field(None, description="会话设置")


class ConversationCreate(ConversationBase):
    """创建会话模式"""

    character_id: uuid.UUID = Field(..., description="角色ID")
    settings: Optional[Dict[str, Any]] = Field(None, description="会话设置")

    @field_validator("title")
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError("会话标题不能为空")
        return v.strip()

    @field_validator("settings")
    def validate_settings(cls, v):
        if v is not None:
            # 验证设置参数
            allowed_keys = {
                "temperature",
                "max_tokens",
                "voice_enabled",
                "language",
                "tone",
                "max_turns",
                "top_p",
                "context_window_size",
                "enable_context_summary",
                "enable_tts",
                "tts_voice",
                "auto_save",
                "enable_rag",
                "rag_threshold",
                "max_rag_results",
                "multi_character_mode",
                "character_response_strategy",
                "enable_character_switching",
                "max_characters",
            }
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"不支持的设置参数: {key}")

            # 验证温度参数
            if "temperature" in v:
                temp = v["temperature"]
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    raise ValueError("温度参数必须在0-2之间")

            # 验证最大令牌数
            if "max_tokens" in v:
                max_tokens = v["max_tokens"]
                if (
                    not isinstance(max_tokens, int)
                    or max_tokens < 1
                    or max_tokens > 4000
                ):
                    raise ValueError("最大令牌数必须在1-4000之间")

            # 验证top_p参数
            if "top_p" in v:
                top_p = v["top_p"]
                if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                    raise ValueError("top_p参数必须在0-1之间")

            # 验证上下文窗口大小
            if "context_window_size" in v:
                window_size = v["context_window_size"]
                if (
                    not isinstance(window_size, int)
                    or window_size < 1
                    or window_size > 50
                ):
                    raise ValueError("上下文窗口大小必须在1-50之间")

            # 验证最大轮数
            if "max_turns" in v:
                max_turns = v["max_turns"]
                if not isinstance(max_turns, int) or max_turns < 1 or max_turns > 100:
                    raise ValueError("最大轮数必须在1-100之间")

            # 验证RAG阈值
            if "rag_threshold" in v:
                rag_threshold = v["rag_threshold"]
                if (
                    not isinstance(rag_threshold, (int, float))
                    or rag_threshold < 0
                    or rag_threshold > 1
                ):
                    raise ValueError("RAG阈值必须在0-1之间")

            # 验证最大RAG结果数
            if "max_rag_results" in v:
                max_rag_results = v["max_rag_results"]
                if (
                    not isinstance(max_rag_results, int)
                    or max_rag_results < 1
                    or max_rag_results > 10
                ):
                    raise ValueError("最大RAG结果数必须在1-10之间")

            # 验证最大角色数量
            if "max_characters" in v:
                max_characters = v["max_characters"]
                if (
                    not isinstance(max_characters, int)
                    or max_characters < 1
                    or max_characters > 10
                ):
                    raise ValueError("最大角色数量必须在1-10之间")

        return v


class ConversationUpdate(SQLModel):
    """更新会话模式"""

    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    status: Optional[ConversationStatus] = Field(None)
    settings: Optional[Dict[str, Any]] = Field(None)

    @field_validator("title")
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("会话标题不能为空")
        return v.strip() if v else v

    @field_validator("settings")
    def validate_settings(cls, v):
        if v is not None:
            # 验证设置参数
            allowed_keys = {
                "temperature",
                "max_tokens",
                "voice_enabled",
                "language",
                "tone",
                "max_turns",
                "top_p",
                "context_window_size",
                "enable_context_summary",
                "enable_tts",
                "tts_voice",
                "auto_save",
                "enable_rag",
                "rag_threshold",
                "max_rag_results",
                "multi_character_mode",
                "character_response_strategy",
                "enable_character_switching",
                "max_characters",
            }
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"不支持的设置参数: {key}")

            # 验证温度参数
            if "temperature" in v:
                temp = v["temperature"]
                if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                    raise ValueError("温度参数必须在0-2之间")

            # 验证最大令牌数
            if "max_tokens" in v:
                max_tokens = v["max_tokens"]
                if (
                    not isinstance(max_tokens, int)
                    or max_tokens < 1
                    or max_tokens > 4000
                ):
                    raise ValueError("最大令牌数必须在1-4000之间")

            # 验证top_p参数
            if "top_p" in v:
                top_p = v["top_p"]
                if not isinstance(top_p, (int, float)) or top_p < 0 or top_p > 1:
                    raise ValueError("top_p参数必须在0-1之间")

            # 验证上下文窗口大小
            if "context_window_size" in v:
                window_size = v["context_window_size"]
                if (
                    not isinstance(window_size, int)
                    or window_size < 1
                    or window_size > 50
                ):
                    raise ValueError("上下文窗口大小必须在1-50之间")

            # 验证最大轮数
            if "max_turns" in v:
                max_turns = v["max_turns"]
                if not isinstance(max_turns, int) or max_turns < 1 or max_turns > 100:
                    raise ValueError("最大轮数必须在1-100之间")

            # 验证RAG阈值
            if "rag_threshold" in v:
                rag_threshold = v["rag_threshold"]
                if (
                    not isinstance(rag_threshold, (int, float))
                    or rag_threshold < 0
                    or rag_threshold > 1
                ):
                    raise ValueError("RAG阈值必须在0-1之间")

            # 验证最大RAG结果数
            if "max_rag_results" in v:
                max_rag_results = v["max_rag_results"]
                if (
                    not isinstance(max_rag_results, int)
                    or max_rag_results < 1
                    or max_rag_results > 10
                ):
                    raise ValueError("最大RAG结果数必须在1-10之间")

            # 验证最大角色数量
            if "max_characters" in v:
                max_characters = v["max_characters"]
                if (
                    not isinstance(max_characters, int)
                    or max_characters < 1
                    or max_characters > 10
                ):
                    raise ValueError("最大角色数量必须在1-10之间")

        return v


class ConversationPublic(ConversationBase):
    """会话公开模式"""

    id: uuid.UUID
    user_id: uuid.UUID
    character_id: uuid.UUID
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ConversationWithDetails(ConversationPublic):
    """带详情的会话模式"""

    character: Optional[CharacterPublic] = Field(None, description="角色信息")
    user: Optional[UserPublic] = Field(None, description="用户信息")


class ConversationListResponse(SQLModel):
    """会话列表响应模式"""

    conversations: List[ConversationWithDetails]
    total: int
    skip: int
    limit: int


class ConversationLookupResponse(SQLModel):
    """会话查找响应模式"""

    exists: bool = Field(..., description="是否存在会话")
    conversation_id: Optional[uuid.UUID] = Field(None, description="会话ID")
    conversation: Optional[ConversationPublic] = Field(None, description="会话详情")


# 消息相关模式
class MessageBase(SQLModel):
    """消息基础模式"""

    content: str = Field(..., description="消息内容")
    content_type: ContentType = Field(ContentType.TEXT, description="内容类型")
    message_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="消息元数据"
    )
    status: MessageStatus = Field(MessageStatus.SENDING, description="消息状态")


class MessageCreate(MessageBase):
    """创建消息模式"""

    sender_type: SenderType = Field(..., description="发送者类型")
    sender_id: Optional[uuid.UUID] = Field(None, description="发送者ID")
    parent_id: Optional[uuid.UUID] = Field(None, description="父消息ID")

    @field_validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("消息内容不能为空")
        if len(v) > 5000:
            raise ValueError("消息内容不能超过5000字符")
        return v.strip()

    @field_validator("message_metadata")
    def validate_message_metadata(cls, v):
        if v:
            # 验证元数据
            allowed_keys = {"length", "language", "sentiment", "confidence"}
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"不支持的元数据字段: {key}")

        return v


class MessageUpdate(SQLModel):
    """更新消息模式"""

    content: Optional[str] = Field(None)
    content_type: Optional[ContentType] = Field(None)
    message_metadata: Optional[Dict[str, Any]] = Field(None)
    status: Optional[MessageStatus] = Field(None)

    @field_validator("content")
    def validate_content(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("消息内容不能为空")
            if len(v) > 5000:
                raise ValueError("消息内容不能超过5000字符")
            return v.strip()
        return v

    @field_validator("message_metadata")
    def validate_message_metadata(cls, v):
        if v is not None:
            # 验证元数据
            allowed_keys = {"length", "language", "sentiment", "confidence"}
            for key in v.keys():
                if key not in allowed_keys:
                    raise ValueError(f"不支持的元数据字段: {key}")

        return v


class MessagePublic(MessageBase):
    """消息公开模式"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    sender_type: SenderType
    sender_id: Optional[uuid.UUID]
    audio_url: Optional[str]
    audio_duration: Optional[int]
    image_url: Optional[str]
    file_url: Optional[str]
    file_size: Optional[int]
    parent_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class MessageListResponse(SQLModel):
    """消息列表响应模式"""

    messages: List[MessagePublic]
    total: int
    skip: int
    limit: int


# 搜索相关模式
class ConversationSearchRequest(SQLModel):
    """会话搜索请求模式"""

    query: Optional[str] = Field(None, description="搜索关键词")
    status: Optional[ConversationStatus] = Field(None, description="会话状态过滤")
    character_id: Optional[uuid.UUID] = Field(None, description="角色ID过滤")
    skip: int = Field(0, ge=0, description="跳过的记录数")
    limit: int = Field(20, ge=1, le=100, description="返回的记录数")
    order_by: str = Field("last_message_at", description="排序字段")
    order: str = Field("desc", description="排序方向")

    @field_validator("query")
    def validate_query(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("搜索关键词至少需要2个字符")
        return v.strip() if v else v

    @field_validator("order_by")
    def validate_order_by(cls, v):
        allowed_fields = {"created_at", "last_message_at", "updated_at", "title"}
        if v not in allowed_fields:
            raise ValueError(f"不支持的排序字段: {v}")
        return v

    @field_validator("order")
    def validate_order(cls, v):
        if v not in {"asc", "desc"}:
            raise ValueError("排序方向必须是asc或desc")
        return v


class MessageSearchRequest(SQLModel):
    """消息搜索请求模式"""

    query: Optional[str] = Field(None, description="搜索关键词")
    sender_type: Optional[SenderType] = Field(None, description="发送者类型过滤")
    content_type: Optional[ContentType] = Field(None, description="内容类型过滤")
    since: Optional[datetime] = Field(None, description="开始时间")
    until: Optional[datetime] = Field(None, description="结束时间")
    skip: int = Field(0, ge=0, description="跳过的记录数")
    limit: int = Field(50, ge=1, le=200, description="返回的记录数")

    @field_validator("query")
    def validate_query(cls, v):
        if v is not None and len(v.strip()) < 2:
            raise ValueError("搜索关键词至少需要2个字符")
        return v.strip() if v else v

    @field_validator("since", "until")
    def validate_datetime(cls, v):
        if v is not None and v > datetime.utcnow():
            raise ValueError("时间不能是未来时间")
        return v


class MessageSearchResponse(SQLModel):
    """消息搜索响应模式"""

    results: List[MessagePublic]
    total: int
    query: Optional[str]
    highlight: Optional[Dict[str, str]] = Field(None, description="高亮显示")


# 会话上下文模式
class ConversationContextBase(SQLModel):
    """会话上下文基础模式"""

    context_type: ContextType = Field(..., description="上下文类型")
    content: str = Field(..., description="上下文内容")
    importance_score: Optional[float] = Field(
        None, ge=0, le=1, description="重要性评分"
    )


class ConversationContextCreate(ConversationContextBase):
    """创建会话上下文模式"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")

    @field_validator("content")
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("上下文内容不能为空")
        if len(v) > 10000:
            raise ValueError("上下文内容不能超过10000字符")
        return v.strip()


class ConversationContextPublic(ConversationContextBase):
    """会话上下文公开模式"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 会话标签模式
class ConversationTagBase(SQLModel):
    """会话标签基础模式"""

    tag_name: str = Field(..., max_length=50, description="标签名称")
    tag_value: Optional[str] = Field(None, max_length=100, description="标签值")


class ConversationTagCreate(ConversationTagBase):
    """创建会话标签模式"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")

    @field_validator("tag_name")
    def validate_tag_name(cls, v):
        if not v or not v.strip():
            raise ValueError("标签名称不能为空")
        return v.strip()


class ConversationTagPublic(ConversationTagBase):
    """会话标签公开模式"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime


# 用户会话限制模式
class UserConversationLimitBase(SQLModel):
    """用户会话限制基础模式"""

    limit_type: str = Field(..., max_length=30, description="限制类型")
    limit_value: int = Field(..., gt=0, description="限制值")
    current_value: int = Field(0, ge=0, description="当前值")
    reset_at: datetime = Field(..., description="重置时间")


class UserConversationLimitCreate(UserConversationLimitBase):
    """创建用户会话限制模式"""

    user_id: uuid.UUID = Field(..., description="用户ID")

    @field_validator("limit_type")
    def validate_limit_type(cls, v):
        allowed_types = {
            "daily_messages",
            "hourly_messages",
            "max_conversations",
            "daily_audio_duration",
        }
        if v not in allowed_types:
            raise ValueError(f"不支持的限制类型: {v}")
        return v


class UserConversationLimitPublic(UserConversationLimitBase):
    """用户会话限制公开模式"""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 统计相关模式
class ConversationStats(SQLModel):
    """会话统计模式"""

    total_messages: int = Field(0, description="总消息数")
    user_messages: int = Field(0, description="用户消息数")
    character_messages: int = Field(0, description="角色消息数")
    text_messages: int = Field(0, description="文本消息数")
    audio_messages: int = Field(0, description="语音消息数")
    image_messages: int = Field(0, description="图片消息数")
    total_duration: int = Field(0, description="总时长（秒）")
    average_message_length: float = Field(0, description="平均消息长度")
    positive_sentiment: float = Field(0, ge=0, le=1, description="积极情感比例")
    neutral_sentiment: float = Field(0, ge=0, le=1, description="中性情感比例")
    negative_sentiment: float = Field(0, ge=0, le=1, description="消极情感比例")
    last_activity_at: Optional[datetime] = Field(None, description="最后活动时间")


class ConversationStatsResponse(SQLModel):
    """会话统计响应模式"""

    conversation_id: uuid.UUID
    stats: ConversationStats
    generated_at: datetime


# 导出相关模式
class ConversationExportRequest(SQLModel):
    """会话导出请求模式"""

    format: str = Field("json", description="导出格式")
    include_metadata: bool = Field(False, description="是否包含元数据")
    date_from: Optional[datetime] = Field(None, description="开始日期")
    date_to: Optional[datetime] = Field(None, description="结束日期")

    @field_validator("format")
    def validate_format(cls, v):
        allowed_formats = {"json", "csv", "txt"}
        if v not in allowed_formats:
            raise ValueError(f"不支持的导出格式: {v}")
        return v


class ConversationExportResponse(SQLModel):
    """会话导出响应模式"""

    download_url: str = Field(..., description="下载链接")
    file_size: int = Field(..., description="文件大小（字节）")
    expires_at: datetime = Field(..., description="过期时间")
