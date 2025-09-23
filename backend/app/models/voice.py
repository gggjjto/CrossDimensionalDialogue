import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlmodel import SQLModel, Field, JSON


class AudioFormat(str, Enum):
    """音频格式枚举"""

    MP3 = "mp3"
    WAV = "wav"
    AAC = "aac"
    OGG = "ogg"
    M4A = "m4a"
    FLAC = "flac"


class AudioQuality(str, Enum):
    """音频质量枚举"""

    LOW = "low"  # 低质量 (8kHz, 16bit)
    MEDIUM = "medium"  # 中等质量 (16kHz, 16bit)
    HIGH = "high"  # 高质量 (44.1kHz, 16bit)
    LOSSLESS = "lossless"  # 无损质量 (44.1kHz, 24bit)


class VoiceLanguage(str, Enum):
    """语音语言枚举"""

    ZH_CN = "zh-cn"  # 中文（简体）
    ZH_TW = "zh-tw"  # 中文（繁体）
    EN_US = "en-us"  # 英语（美式）
    EN_GB = "en-gb"  # 英语（英式）
    JA_JP = "ja-jp"  # 日语
    KO_KR = "ko-kr"  # 韩语
    ES_ES = "es-es"  # 西班牙语
    FR_FR = "fr-fr"  # 法语
    DE_DE = "de-de"  # 德语
    RU_RU = "ru-ru"  # 俄语


class VoiceGender(str, Enum):
    """语音性别枚举"""

    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class VoiceEmotion(str, Enum):
    """语音情感枚举"""

    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CALM = "calm"
    CONFUSED = "confused"
    SURPRISED = "surprised"


class AudioProcessingStatus(str, Enum):
    """音频处理状态枚举"""

    PENDING = "pending"  # 等待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 处理完成
    FAILED = "failed"  # 处理失败
    CANCELLED = "cancelled"  # 已取消


class VoiceMessageType(str, Enum):
    """语音消息类型枚举"""

    USER_INPUT = "user_input"  # 用户语音输入
    CHARACTER_REPLY = "character_reply"  # 角色语音回复
    SYSTEM_ANNOUNCEMENT = "system_announcement"  # 系统语音通知


# 语音消息模型
class VoiceMessageBase(SQLModel):
    """语音消息基础模型"""

    message_id: uuid.UUID = Field(..., description="关联的消息ID")
    voice_type: VoiceMessageType = Field(..., description="语音消息类型")
    audio_url: str = Field(..., max_length=500, description="音频文件URL")
    audio_format: AudioFormat = Field(..., description="音频格式")
    audio_quality: AudioQuality = Field(..., description="音频质量")
    duration: float = Field(..., ge=0, description="音频时长（秒）")
    file_size: int = Field(..., ge=0, description="文件大小（字节）")
    language: VoiceLanguage = Field(..., description="语音语言")
    gender: Optional[VoiceGender] = Field(None, description="语音性别")
    emotion: Optional[VoiceEmotion] = Field(None, description="语音情感")
    processing_status: AudioProcessingStatus = Field(
        AudioProcessingStatus.PENDING, description="处理状态"
    )
    transcription: Optional[str] = Field(None, description="转录文本")
    confidence_score: Optional[float] = Field(
        None, ge=0, le=1, description="置信度分数"
    )
    voice_metadata: Optional[Dict[str, Any]] = Field(
        None, sa_type=JSON, description="元数据"
    )


class VoiceMessageCreate(VoiceMessageBase):
    """创建语音消息模型"""

    pass


class VoiceMessage(VoiceMessageBase, table=True):
    """语音消息表模型"""

    __tablename__ = "voice_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )
    processed_at: Optional[datetime] = Field(None, description="处理完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")


class VoiceMessagePublic(VoiceMessageBase):
    """语音消息公开模型"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime]
    error_message: Optional[str]


# 语音配置模型
class VoiceConfigBase(SQLModel):
    """语音配置基础模型"""

    character_id: uuid.UUID = Field(..., description="角色ID")
    voice_name: str = Field(..., max_length=100, description="语音名称")
    voice_id: str = Field(..., max_length=100, description="语音ID")
    language: VoiceLanguage = Field(..., description="语音语言")
    gender: VoiceGender = Field(..., description="语音性别")
    speed: float = Field(1.0, ge=0.5, le=2.0, description="语速")
    pitch: float = Field(1.0, ge=0.5, le=2.0, description="音调")
    volume: float = Field(1.0, ge=0.0, le=1.0, description="音量")
    emotion: VoiceEmotion = Field(VoiceEmotion.NEUTRAL, description="默认情感")
    is_active: bool = Field(True, description="是否激活")
    config_metadata: Optional[Dict[str, Any]] = Field(
        None, sa_type=JSON, description="配置元数据"
    )


class VoiceConfigCreate(VoiceConfigBase):
    """创建语音配置模型"""

    pass


class VoiceConfigUpdate(SQLModel):
    """更新语音配置模型"""

    voice_name: Optional[str] = Field(None, max_length=100)
    voice_id: Optional[str] = Field(None, max_length=100)
    language: Optional[VoiceLanguage] = Field(None)
    gender: Optional[VoiceGender] = Field(None)
    speed: Optional[float] = Field(None, ge=0.5, le=2.0)
    pitch: Optional[float] = Field(None, ge=0.5, le=2.0)
    volume: Optional[float] = Field(None, ge=0.0, le=1.0)
    emotion: Optional[VoiceEmotion] = Field(None)
    is_active: Optional[bool] = Field(None)
    config_metadata: Optional[Dict[str, Any]] = Field(None, sa_type=JSON)


class VoiceConfig(VoiceConfigBase, table=True):
    """语音配置表模型"""

    __tablename__ = "voice_configs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )


class VoiceConfigPublic(VoiceConfigBase):
    """语音配置公开模型"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 音频处理任务模型
class AudioProcessingTaskBase(SQLModel):
    """音频处理任务基础模型"""

    task_type: str = Field(..., max_length=50, description="任务类型")
    input_file_url: str = Field(..., max_length=500, description="输入文件URL")
    output_file_url: Optional[str] = Field(
        None, max_length=500, description="输出文件URL"
    )
    status: AudioProcessingStatus = Field(
        AudioProcessingStatus.PENDING, description="任务状态"
    )
    progress: float = Field(0.0, ge=0.0, le=100.0, description="处理进度（百分比）")
    parameters: Optional[Dict[str, Any]] = Field(
        None, sa_type=JSON, description="处理参数"
    )
    result: Optional[Dict[str, Any]] = Field(None, sa_type=JSON, description="处理结果")
    error_message: Optional[str] = Field(None, description="错误信息")
    retry_count: int = Field(0, ge=0, description="重试次数")
    max_retries: int = Field(3, ge=0, description="最大重试次数")


class AudioProcessingTaskCreate(AudioProcessingTaskBase):
    """创建音频处理任务模型"""

    pass


class AudioProcessingTask(AudioProcessingTaskBase, table=True):
    """音频处理任务表模型"""

    __tablename__ = "audio_processing_tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )
    started_at: Optional[datetime] = Field(None, description="开始处理时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class AudioProcessingTaskPublic(AudioProcessingTaskBase):
    """音频处理任务公开模型"""

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


# 语音识别结果模型
class SpeechRecognitionResult(SQLModel):
    """语音识别结果模型"""

    text: str = Field(..., description="识别文本")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    language: VoiceLanguage = Field(..., description="识别语言")
    duration: float = Field(..., ge=0, description="音频时长")
    word_count: int = Field(..., ge=0, description="词数")
    segments: Optional[List[Dict[str, Any]]] = Field(
        None, sa_type=JSON, description="分段结果"
    )
    voice_metadata: Optional[Dict[str, Any]] = Field(
        None, sa_type=JSON, description="元数据"
    )


# 语音合成请求模型
class VoiceSynthesisRequest(SQLModel):
    """语音合成请求模型"""

    text: str = Field(..., description="要合成的文本")
    voice_config_id: uuid.UUID = Field(..., description="语音配置ID")
    emotion: Optional[VoiceEmotion] = Field(None, description="情感")
    speed: Optional[float] = Field(None, ge=0.5, le=2.0, description="语速")
    pitch: Optional[float] = Field(None, ge=0.5, le=2.0, description="音调")
    volume: Optional[float] = Field(None, ge=0.0, le=1.0, description="音量")
    output_format: AudioFormat = Field(AudioFormat.MP3, description="输出格式")
    output_quality: AudioQuality = Field(AudioQuality.MEDIUM, description="输出质量")


# 语音合成结果模型
class VoiceSynthesisResult(SQLModel):
    """语音合成结果模型"""

    audio_url: str = Field(..., description="生成的音频URL")
    duration: float = Field(..., ge=0, description="音频时长")
    file_size: int = Field(..., ge=0, description="文件大小")
    format: AudioFormat = Field(..., description="音频格式")
    quality: AudioQuality = Field(..., description="音频质量")
    voice_metadata: Optional[Dict[str, Any]] = Field(
        None, sa_type=JSON, description="元数据"
    )


# 音频质量检测结果模型
class AudioQualityReport(SQLModel):
    """音频质量检测报告模型"""

    overall_score: float = Field(..., ge=0, le=10, description="总体质量分数")
    clarity_score: float = Field(..., ge=0, le=10, description="清晰度分数")
    volume_score: float = Field(..., ge=0, le=10, description="音量分数")
    noise_level: float = Field(..., ge=0, le=10, description="噪音水平")
    sample_rate: int = Field(..., ge=0, description="采样率")
    bit_depth: int = Field(..., ge=0, description="位深度")
    channels: int = Field(..., ge=1, description="声道数")
    duration: float = Field(..., ge=0, description="时长")
    file_size: int = Field(..., ge=0, description="文件大小")
    format: AudioFormat = Field(..., description="音频格式")
    issues: List[str] = Field(default_factory=list, description="检测到的问题")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")


# 语音消息统计模型
class VoiceMessageStats(SQLModel):
    """语音消息统计模型"""

    total_voice_messages: int = Field(0, description="总语音消息数")
    user_voice_messages: int = Field(0, description="用户语音消息数")
    character_voice_messages: int = Field(0, description="角色语音消息数")
    total_duration: float = Field(0, description="总时长（秒）")
    average_duration: float = Field(0, description="平均时长（秒）")
    total_file_size: int = Field(0, description="总文件大小（字节）")
    average_file_size: int = Field(0, description="平均文件大小（字节）")
    processing_success_rate: float = Field(0, ge=0, le=1, description="处理成功率")
    most_used_language: Optional[VoiceLanguage] = Field(None, description="最常用语言")
    most_used_format: Optional[AudioFormat] = Field(None, description="最常用格式")


# 响应模型
class VoiceMessageListResponse(SQLModel):
    """语音消息列表响应模型"""

    voice_messages: List[VoiceMessagePublic]
    total: int
    skip: int
    limit: int


class VoiceConfigListResponse(SQLModel):
    """语音配置列表响应模型"""

    voice_configs: List[VoiceConfigPublic]
    total: int
    skip: int
    limit: int


class AudioProcessingTaskListResponse(SQLModel):
    """音频处理任务列表响应模型"""

    tasks: List[AudioProcessingTaskPublic]
    total: int
    skip: int
    limit: int
