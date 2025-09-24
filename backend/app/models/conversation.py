import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field, JSON

if TYPE_CHECKING:
    from app.models.user import User, UserPublic
    from app.models.character import Character, CharacterPublic


class ConversationStatus(str, Enum):
    """会话状态枚举"""

    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"
    ARCHIVED = "archived"


class SenderType(str, Enum):
    """发送者类型枚举"""

    USER = "user"
    CHARACTER = "character"
    SYSTEM = "system"


class ContentType(str, Enum):
    """内容类型枚举"""

    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    FILE = "file"


class MessageStatus(str, Enum):
    """消息状态枚举"""

    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    DELETED = "deleted"


class ContextType(str, Enum):
    """上下文类型枚举"""

    SUMMARY = "summary"
    MEMORY = "memory"
    KEY_POINTS = "key_points"
    EMOTION = "emotion"


class LLMProvider(str, Enum):
    """LLM提供商枚举"""

    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    LOCAL = "local"


class MultiCharacterMode(str, Enum):
    """多角色模式枚举"""

    SINGLE = "single"  # 单角色模式
    MULTIPLE = "multiple"  # 多角色模式
    SWITCHING = "switching"  # 角色切换模式


class CharacterResponseStrategy(str, Enum):
    """角色回复策略枚举"""

    ROUND_ROBIN = "round_robin"  # 轮流回复
    PRIORITY_BASED = "priority_based"  # 基于优先级
    CONTEXT_AWARE = "context_aware"  # 基于上下文
    USER_CHOICE = "user_choice"  # 用户选择


class ConversationSettings(SQLModel):
    """会话设置模型"""

    # LLM配置
    llm_provider: LLMProvider = Field(
        default=LLMProvider.QWEN, description="LLM提供商"
    )
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM模型")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="温度参数")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="最大token数")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="top_p参数")

    # 多角色配置
    multi_character_mode: MultiCharacterMode = Field(
        default=MultiCharacterMode.SINGLE, description="多角色模式"
    )
    character_response_strategy: CharacterResponseStrategy = Field(
        default=CharacterResponseStrategy.CONTEXT_AWARE, description="角色回复策略"
    )
    enable_character_switching: bool = Field(
        default=False, description="是否启用角色切换"
    )
    max_characters: int = Field(default=3, ge=1, le=10, description="最大角色数量")

    # 上下文配置
    context_window_size: int = Field(
        default=10, ge=1, le=50, description="上下文窗口大小"
    )
    enable_context_summary: bool = Field(
        default=False, description="是否启用上下文摘要"
    )
    context_summary_threshold: int = Field(
        default=15, ge=5, le=50, description="上下文摘要阈值"
    )

    # RAG配置
    enable_rag: bool = Field(default=False, description="是否启用RAG")
    rag_threshold: float = Field(
        default=0.7, ge=0.0, le=1.0, description="RAG相关性阈值"
    )
    max_rag_results: int = Field(default=3, ge=1, le=10, description="最大RAG结果数")

    # 语音配置
    enable_tts: bool = Field(default=False, description="是否启用TTS")
    tts_voice: Optional[str] = Field(default=None, description="TTS音色")

    # 其他配置
    auto_save: bool = Field(default=True, description="是否自动保存")
    enable_typing_indicator: bool = Field(default=True, description="是否显示输入状态")


# 多角色会话模型
class MultiCharacterConversation(SQLModel, table=True):
    """多角色会话模型"""

    __tablename__ = "multi_character_conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id", description="关联的会话ID"
    )
    character_id: uuid.UUID = Field(foreign_key="characters.id", description="角色ID")
    priority: int = Field(default=1, ge=1, le=10, description="角色优先级")
    is_active: bool = Field(default=True, description="是否激活")
    last_response_at: Optional[datetime] = Field(
        default=None, description="最后回复时间"
    )
    response_count: int = Field(default=0, description="回复次数")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# 会话相关模型
class ConversationBase(SQLModel):
    """会话基础模型"""

    title: str = Field(max_length=255, description="会话标题")
    description: Optional[str] = Field(default=None, description="会话描述")
    status: ConversationStatus = Field(
        default=ConversationStatus.ACTIVE, description="会话状态"
    )
    settings: Optional[dict] = Field(default=None, sa_type=JSON, description="会话设置")


class ConversationCreate(ConversationBase):
    """创建会话模型"""

    character_id: uuid.UUID = Field(description="角色ID")
    settings: Optional[dict] = Field(default=None, sa_type=JSON, description="会话设置")


class ConversationUpdate(SQLModel):
    """更新会话模型"""

    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None)
    status: Optional[ConversationStatus] = Field(default=None)
    settings: Optional[dict] = Field(default=None, sa_type=JSON)


class Conversation(ConversationBase, table=True):
    """会话表模型"""

    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", description="用户ID")
    character_id: uuid.UUID = Field(foreign_key="characters.id", description="角色ID")
    message_count: int = Field(default=0, description="消息总数")
    last_message_at: Optional[datetime] = Field(
        default=None, description="最后消息时间"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )
    deleted_at: Optional[datetime] = Field(default=None, description="软删除时间")

    # 关系
    user: Optional["User"] = Relationship(back_populates="conversations")
    character: Optional["Character"] = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )
    contexts: List["ConversationContext"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )
    tags: List["ConversationTag"] = Relationship(
        back_populates="conversation", cascade_delete=True
    )


class ConversationPublic(ConversationBase):
    """会话公开模型"""

    id: uuid.UUID
    user_id: uuid.UUID
    character_id: uuid.UUID
    message_count: int
    last_message_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class ConversationWithDetails(ConversationPublic):
    """带详情的会话模型"""

    character: Optional["CharacterPublic"] = Field(default=None, description="角色信息")
    user: Optional["UserPublic"] = Field(default=None, description="用户信息")


# 消息相关模型
class MessageBase(SQLModel):
    """消息基础模型"""

    content: str = Field(description="消息内容")
    content_type: ContentType = Field(default=ContentType.TEXT, description="内容类型")
    message_metadata: Optional[dict] = Field(default=None, description="消息元数据")
    status: MessageStatus = Field(default=MessageStatus.SENDING, description="消息状态")


class MessageCreate(MessageBase):
    """创建消息模型"""

    sender_type: SenderType = Field(description="发送者类型")
    sender_id: Optional[uuid.UUID] = Field(default=None, description="发送者ID")
    parent_id: Optional[uuid.UUID] = Field(default=None, description="父消息ID")


class MessageUpdate(SQLModel):
    """更新消息模型"""

    content: Optional[str] = Field(default=None)
    content_type: Optional[ContentType] = Field(default=None)
    message_metadata: Optional[dict] = Field(default=None)
    status: Optional[MessageStatus] = Field(default=None)


class Message(MessageBase, table=True):
    """消息表模型"""

    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id", description="会话ID"
    )
    sender_type: SenderType = Field(description="发送者类型")
    sender_id: Optional[uuid.UUID] = Field(default=None, description="发送者ID")
    audio_url: Optional[str] = Field(
        default=None, max_length=500, description="音频文件URL"
    )
    audio_duration: Optional[int] = Field(default=None, description="音频时长（秒）")
    image_url: Optional[str] = Field(
        default=None, max_length=500, description="图片文件URL"
    )
    file_url: Optional[str] = Field(default=None, max_length=500, description="文件URL")
    file_size: Optional[int] = Field(default=None, description="文件大小（字节）")
    message_metadata: Optional[dict] = Field(
        default=None, sa_type=JSON, description="消息元数据"
    )
    parent_id: Optional[uuid.UUID] = Field(
        foreign_key="messages.id", default=None, description="父消息ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )

    # 关系
    conversation: Optional["Conversation"] = Relationship(back_populates="messages")
    parent: Optional["Message"] = Relationship(
        back_populates="replies", sa_relationship_kwargs={"remote_side": "Message.id"}
    )
    replies: List["Message"] = Relationship(back_populates="parent")


class MessagePublic(MessageBase):
    """消息公开模型"""

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


# 会话上下文模型
class ConversationContextBase(SQLModel):
    """会话上下文基础模型"""

    context_type: ContextType = Field(description="上下文类型")
    content: str = Field(description="上下文内容")
    importance_score: Optional[float] = Field(
        default=None, ge=0, le=1, description="重要性评分"
    )


class ConversationContextCreate(ConversationContextBase):
    """创建会话上下文模型"""

    conversation_id: uuid.UUID = Field(description="会话ID")


class ConversationContext(ConversationContextBase, table=True):
    """会话上下文表模型"""

    __tablename__ = "conversation_contexts"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id", description="会话ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )

    # 关系
    conversation: Optional["Conversation"] = Relationship(back_populates="contexts")


class ConversationContextPublic(ConversationContextBase):
    """会话上下文公开模型"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 会话标签模型
class ConversationTagBase(SQLModel):
    """会话标签基础模型"""

    tag_name: str = Field(max_length=50, description="标签名称")
    tag_value: Optional[str] = Field(default=None, max_length=100, description="标签值")


class ConversationTagCreate(ConversationTagBase):
    """创建会话标签模型"""

    conversation_id: uuid.UUID = Field(description="会话ID")


class ConversationTag(ConversationTagBase, table=True):
    """会话标签表模型"""

    __tablename__ = "conversation_tags"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(
        foreign_key="conversations.id", description="会话ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )

    # 关系
    conversation: Optional["Conversation"] = Relationship(back_populates="tags")


class ConversationTagPublic(ConversationTagBase):
    """会话标签公开模型"""

    id: uuid.UUID
    conversation_id: uuid.UUID
    created_at: datetime


# 用户会话限制模型
class UserConversationLimitBase(SQLModel):
    """用户会话限制基础模型"""

    limit_type: str = Field(max_length=30, description="限制类型")
    limit_value: int = Field(gt=0, description="限制值")
    current_value: int = Field(default=0, ge=0, description="当前值")
    reset_at: datetime = Field(description="重置时间")


class UserConversationLimitCreate(UserConversationLimitBase):
    """创建用户会话限制模型"""

    user_id: uuid.UUID = Field(description="用户ID")


class UserConversationLimit(UserConversationLimitBase, table=True):
    """用户会话限制表模型"""

    __tablename__ = "user_conversation_limits"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", description="用户ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )


class UserConversationLimitPublic(UserConversationLimitBase):
    """用户会话限制公开模型"""

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 分页和搜索模型
class ConversationListResponse(SQLModel):
    """会话列表响应模型"""

    conversations: List[ConversationWithDetails]
    total: int
    skip: int
    limit: int


class MessageListResponse(SQLModel):
    """消息列表响应模型"""

    messages: List[MessagePublic]
    total: int
    skip: int
    limit: int


class ConversationSearchRequest(SQLModel):
    """会话搜索请求模型"""

    query: Optional[str] = Field(default=None, description="搜索关键词")
    status: Optional[ConversationStatus] = Field(
        default=None, description="会话状态过滤"
    )
    character_id: Optional[uuid.UUID] = Field(default=None, description="角色ID过滤")
    skip: int = Field(default=0, ge=0, description="跳过的记录数")
    limit: int = Field(default=20, ge=1, le=100, description="返回的记录数")
    order_by: str = Field(default="last_message_at", description="排序字段")
    order: str = Field(default="desc", description="排序方向")


class MessageSearchRequest(SQLModel):
    """消息搜索请求模型"""

    query: Optional[str] = Field(default=None, description="搜索关键词")
    sender_type: Optional[SenderType] = Field(
        default=None, description="发送者类型过滤"
    )
    content_type: Optional[ContentType] = Field(
        default=None, description="内容类型过滤"
    )
    since: Optional[datetime] = Field(default=None, description="开始时间")
    until: Optional[datetime] = Field(default=None, description="结束时间")
    skip: int = Field(default=0, ge=0, description="跳过的记录数")
    limit: int = Field(default=50, ge=1, le=200, description="返回的记录数")
