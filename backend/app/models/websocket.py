import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from enum import Enum

from sqlmodel import SQLModel, Field


class WebSocketMessageType(str, Enum):
    """WebSocket消息类型枚举"""

    # 连接管理
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"

    # 消息相关
    MESSAGE_SEND = "message_send"
    MESSAGE_RECEIVE = "message_receive"
    MESSAGE_UPDATE = "message_update"
    MESSAGE_DELETE = "message_delete"

    # 输入状态
    TYPING_START = "typing_start"
    TYPING_STOP = "typing_stop"

    # 会话相关
    CONVERSATION_CREATE = "conversation_create"
    CONVERSATION_UPDATE = "conversation_update"
    CONVERSATION_DELETE = "conversation_delete"

    # 系统通知
    SYSTEM_NOTIFICATION = "system_notification"
    ERROR = "error"

    # 语音消息相关
    VOICE_MESSAGE = "voice_message"  # 语音消息
    VOICE_UPLOAD_START = "voice_upload_start"  # 开始上传语音
    VOICE_UPLOAD_PROGRESS = "voice_upload_progress"  # 语音上传进度
    VOICE_UPLOAD_COMPLETE = "voice_upload_complete"  # 语音上传完成
    VOICE_PROCESSING_START = "voice_processing_start"  # 开始处理语音
    VOICE_PROCESSING_PROGRESS = "voice_processing_progress"  # 语音处理进度
    VOICE_PROCESSING_COMPLETE = "voice_processing_complete"  # 语音处理完成
    VOICE_SYNTHESIS_START = "voice_synthesis_start"  # 开始语音合成
    VOICE_SYNTHESIS_PROGRESS = "voice_synthesis_progress"  # 语音合成进度
    VOICE_SYNTHESIS_COMPLETE = "voice_synthesis_complete"  # 语音合成完成
    VOICE_QUALITY_CHECK = "voice_quality_check"  # 语音质量检测
    VOICE_ERROR = "voice_error"  # 语音处理错误


class WebSocketConnectionStatus(str, Enum):
    """WebSocket连接状态枚举"""

    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


class WebSocketMessageBase(SQLModel):
    """WebSocket消息基础模型"""

    type: WebSocketMessageType = Field(..., description="消息类型")
    data: Dict[str, Any] = Field(..., description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class WebSocketMessage(WebSocketMessageBase):
    """WebSocket消息模型"""

    id: str = Field(..., description="消息ID")
    conversation_id: Optional[uuid.UUID] = Field(None, description="会话ID")
    user_id: Optional[uuid.UUID] = Field(None, description="用户ID")


class WebSocketMessageCreate(WebSocketMessageBase):
    """创建WebSocket消息模型"""

    conversation_id: Optional[uuid.UUID] = Field(None, description="会话ID")
    user_id: Optional[uuid.UUID] = Field(None, description="用户ID")


class WebSocketMessageResponse(WebSocketMessageBase):
    """WebSocket消息响应模型"""

    id: str
    conversation_id: Optional[uuid.UUID]
    user_id: Optional[uuid.UUID]
    success: bool = Field(True, description="是否成功")
    error: Optional[str] = Field(None, description="错误信息")


class RealtimeMessage(SQLModel):
    """实时消息模型"""

    id: str = Field(..., description="消息ID")
    conversation_id: uuid.UUID = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    content_type: str = Field(..., description="内容类型")
    sender_type: str = Field(..., description="发送者类型")
    sender_id: uuid.UUID = Field(..., description="发送者ID")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")
    status: str = Field(..., description="消息状态")
    created_at: datetime = Field(..., description="创建时间")


class RealtimeMessageCreate(SQLModel):
    """创建实时消息模型"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")
    content: str = Field(..., description="消息内容")
    content_type: str = Field(..., description="内容类型")
    sender_type: str = Field(..., description="发送者类型")
    sender_id: uuid.UUID = Field(..., description="发送者ID")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")


class UserOnlineStatus(SQLModel):
    """用户在线状态模型"""

    user_id: uuid.UUID = Field(..., description="用户ID")
    is_online: bool = Field(..., description="是否在线")
    last_seen: datetime = Field(..., description="最后在线时间")
    connection_count: int = Field(0, description="连接数量")


class TypingStatus(SQLModel):
    """输入状态模型"""

    user_id: uuid.UUID = Field(..., description="用户ID")
    conversation_id: uuid.UUID = Field(..., description="会话ID")
    is_typing: bool = Field(..., description="是否正在输入")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class MessageBroadcast(SQLModel):
    """消息广播模型"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")
    message: RealtimeMessage = Field(..., description="消息")
    exclude_user: Optional[uuid.UUID] = Field(None, description="排除的用户")


class SystemNotification(SQLModel):
    """系统通知模型"""

    notification_type: str = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    message: str = Field(..., description="通知内容")
    target_users: List[uuid.UUID] = Field(default_factory=list, description="目标用户")
    target_conversations: List[uuid.UUID] = Field(
        default_factory=list, description="目标会话"
    )
    data: Optional[Dict[str, Any]] = Field(None, description="附加数据")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )


class WebSocketError(SQLModel):
    """WebSocket错误模型"""

    error_type: str = Field(..., description="错误类型")
    error_message: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class WebSocketConnectionInfo(SQLModel):
    """WebSocket连接信息模型"""

    connection_id: str = Field(..., description="连接ID")
    user_id: uuid.UUID = Field(..., description="用户ID")
    conversation_id: Optional[uuid.UUID] = Field(None, description="会话ID")
    status: WebSocketConnectionStatus = Field(..., description="连接状态")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="用户代理")
    connected_at: datetime = Field(..., description="连接时间")
    last_ping: Optional[datetime] = Field(None, description="最后ping时间")
    last_pong: Optional[datetime] = Field(None, description="最后pong时间")


# 语音消息相关的WebSocket数据模型
class VoiceMessageData(SQLModel):
    """语音消息数据模型"""

    message_id: uuid.UUID = Field(..., description="消息ID")
    conversation_id: uuid.UUID = Field(..., description="会话ID")
    sender_id: uuid.UUID = Field(..., description="发送者ID")
    sender_type: str = Field(..., description="发送者类型")
    audio_url: str = Field(..., description="音频文件URL")
    audio_format: str = Field(..., description="音频格式")
    duration: float = Field(..., description="音频时长")
    file_size: int = Field(..., description="文件大小")
    language: str = Field(..., description="语音语言")
    transcription: Optional[str] = Field(None, description="转录文本")
    confidence: Optional[float] = Field(None, description="置信度")
    processing_status: str = Field(..., description="处理状态")


class VoiceUploadProgressData(SQLModel):
    """语音上传进度数据模型"""

    file_id: str = Field(..., description="文件ID")
    progress: float = Field(..., ge=0, le=100, description="上传进度百分比")
    bytes_uploaded: int = Field(..., description="已上传字节数")
    total_bytes: int = Field(..., description="总字节数")
    estimated_time_remaining: Optional[int] = Field(
        None, description="预计剩余时间（秒）"
    )


class VoiceProcessingProgressData(SQLModel):
    """语音处理进度数据模型"""

    task_id: uuid.UUID = Field(..., description="任务ID")
    file_id: str = Field(..., description="文件ID")
    processing_type: str = Field(..., description="处理类型")
    progress: float = Field(..., ge=0, le=100, description="处理进度百分比")
    status: str = Field(..., description="处理状态")
    estimated_time_remaining: Optional[int] = Field(
        None, description="预计剩余时间（秒）"
    )
    result: Optional[Dict[str, Any]] = Field(None, description="处理结果")


class VoiceSynthesisProgressData(SQLModel):
    """语音合成进度数据模型"""

    synthesis_id: str = Field(..., description="合成ID")
    text: str = Field(..., description="待合成文本")
    progress: float = Field(..., ge=0, le=100, description="合成进度百分比")
    status: str = Field(..., description="合成状态")
    estimated_time_remaining: Optional[int] = Field(
        None, description="预计剩余时间（秒）"
    )
    audio_url: Optional[str] = Field(None, description="合成音频URL")


class VoiceQualityCheckData(SQLModel):
    """语音质量检测数据模型"""

    file_id: str = Field(..., description="文件ID")
    quality_score: float = Field(..., ge=0, le=10, description="质量评分")
    duration: float = Field(..., description="音频时长")
    sample_rate: int = Field(..., description="采样率")
    rms: float = Field(..., description="RMS值")
    zero_crossing_rate: float = Field(..., description="零交叉率")
    issues: List[str] = Field(default_factory=list, description="检测到的问题")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")
    is_good_quality: bool = Field(..., description="是否质量良好")


class VoiceErrorData(SQLModel):
    """语音处理错误数据模型"""

    error_type: str = Field(..., description="错误类型")
    error_code: str = Field(..., description="错误代码")
    error_message: str = Field(..., description="错误信息")
    file_id: Optional[str] = Field(None, description="相关文件ID")
    task_id: Optional[uuid.UUID] = Field(None, description="相关任务ID")
    retry_count: int = Field(0, description="重试次数")
    can_retry: bool = Field(True, description="是否可以重试")
