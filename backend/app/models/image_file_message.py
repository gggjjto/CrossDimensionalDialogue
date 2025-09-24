"""
图片和文件消息相关模型
"""

import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

from sqlmodel import Relationship, SQLModel, Field, JSON

if TYPE_CHECKING:
    from app.models.conversation import Message


class ImageFormat(str, Enum):
    """图片格式枚举"""

    JPEG = "jpeg"
    PNG = "png"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"


class FileType(str, Enum):
    """文件类型枚举"""

    DOCUMENT = "document"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    ARCHIVE = "archive"
    OTHER = "other"


class ProcessingStatus(str, Enum):
    """处理状态枚举"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SecurityScanStatus(str, Enum):
    """安全扫描状态枚举"""

    PENDING = "pending"
    SCANNING = "scanning"
    SAFE = "safe"
    UNSAFE = "unsafe"
    FAILED = "failed"


class TaskType(str, Enum):
    """任务类型枚举"""

    IMAGE_COMPRESS = "image_compress"
    IMAGE_RESIZE = "image_resize"
    IMAGE_FORMAT_CONVERT = "image_format_convert"
    FILE_SCAN = "file_scan"
    THUMBNAIL_GENERATE = "thumbnail_generate"


# 图片消息模型
class ImageMessageBase(SQLModel):
    """图片消息基础模型"""

    file_url: str = Field(max_length=500, description="文件URL")
    file_name: str = Field(max_length=255, description="文件名")
    file_size: int = Field(gt=0, description="文件大小（字节）")
    mime_type: str = Field(max_length=100, description="MIME类型")
    width: Optional[int] = Field(default=None, gt=0, description="图片宽度")
    height: Optional[int] = Field(default=None, gt=0, description="图片高度")
    format: ImageFormat = Field(description="图片格式")
    quality_score: Optional[float] = Field(
        default=None, ge=0, le=1, description="质量评分"
    )
    thumbnail_url: Optional[str] = Field(
        default=None, max_length=500, description="缩略图URL"
    )
    compressed_url: Optional[str] = Field(
        default=None, max_length=500, description="压缩图片URL"
    )
    image_metadata: Optional[dict] = Field(
        default=None, sa_type=JSON, description="元数据"
    )
    processing_status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING, description="处理状态"
    )


class ImageMessageCreate(ImageMessageBase):
    """创建图片消息模型"""

    message_id: uuid.UUID = Field(description="关联的消息ID")


class ImageMessageUpdate(SQLModel):
    """更新图片消息模型"""

    file_url: Optional[str] = Field(default=None, max_length=500)
    file_name: Optional[str] = Field(default=None, max_length=255)
    width: Optional[int] = Field(default=None, gt=0)
    height: Optional[int] = Field(default=None, gt=0)
    quality_score: Optional[float] = Field(default=None, ge=0, le=1)
    thumbnail_url: Optional[str] = Field(default=None, max_length=500)
    compressed_url: Optional[str] = Field(default=None, max_length=500)
    image_metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    processing_status: Optional[ProcessingStatus] = Field(default=None)


class ImageMessage(ImageMessageBase, table=True):
    """图片消息表模型"""

    __tablename__ = "image_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="messages.id", description="关联的消息ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )

    # 关系
    message: Optional["Message"] = Relationship(back_populates="image_message")


class ImageMessagePublic(ImageMessageBase):
    """图片消息公开模型"""

    id: uuid.UUID
    message_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 文件消息模型
class FileMessageBase(SQLModel):
    """文件消息基础模型"""

    file_url: str = Field(max_length=500, description="文件URL")
    file_name: str = Field(max_length=255, description="文件名")
    file_size: int = Field(gt=0, description="文件大小（字节）")
    mime_type: str = Field(max_length=100, description="MIME类型")
    file_extension: str = Field(max_length=20, description="文件扩展名")
    file_type: FileType = Field(description="文件类型")
    checksum: Optional[str] = Field(
        default=None, max_length=64, description="文件校验和"
    )
    image_metadata: Optional[dict] = Field(
        default=None, sa_type=JSON, description="元数据"
    )
    preview_url: Optional[str] = Field(
        default=None, max_length=500, description="预览URL"
    )
    download_count: int = Field(default=0, description="下载次数")
    processing_status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING, description="处理状态"
    )
    security_scan_status: SecurityScanStatus = Field(
        default=SecurityScanStatus.PENDING, description="安全扫描状态"
    )


class FileMessageCreate(FileMessageBase):
    """创建文件消息模型"""

    message_id: uuid.UUID = Field(description="关联的消息ID")


class FileMessageUpdate(SQLModel):
    """更新文件消息模型"""

    file_url: Optional[str] = Field(default=None, max_length=500)
    file_name: Optional[str] = Field(default=None, max_length=255)
    checksum: Optional[str] = Field(default=None, max_length=64)
    image_metadata: Optional[dict] = Field(default=None, sa_type=JSON)
    preview_url: Optional[str] = Field(default=None, max_length=500)
    download_count: Optional[int] = Field(default=None)
    processing_status: Optional[ProcessingStatus] = Field(default=None)
    security_scan_status: Optional[SecurityScanStatus] = Field(default=None)


class FileMessage(FileMessageBase, table=True):
    """文件消息表模型"""

    __tablename__ = "file_messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    message_id: uuid.UUID = Field(foreign_key="messages.id", description="关联的消息ID")
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="更新时间"
    )

    # 关系
    message: Optional["Message"] = Relationship(back_populates="file_message")


class FileMessagePublic(FileMessageBase):
    """文件消息公开模型"""

    id: uuid.UUID
    message_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# 文件处理任务模型
class FileProcessingTaskBase(SQLModel):
    """文件处理任务基础模型"""

    task_type: TaskType = Field(description="任务类型")
    status: ProcessingStatus = Field(
        default=ProcessingStatus.PENDING, description="任务状态"
    )
    progress: int = Field(default=0, ge=0, le=100, description="进度百分比")
    error_message: Optional[str] = Field(default=None, description="错误信息")
    result_data: Optional[dict] = Field(
        default=None, sa_type=JSON, description="结果数据"
    )
    started_at: Optional[datetime] = Field(default=None, description="开始时间")
    completed_at: Optional[datetime] = Field(default=None, description="完成时间")


class FileProcessingTaskCreate(FileProcessingTaskBase):
    """创建文件处理任务模型"""

    file_message_id: Optional[uuid.UUID] = Field(
        default=None, description="关联的文件消息ID"
    )
    image_message_id: Optional[uuid.UUID] = Field(
        default=None, description="关联的图片消息ID"
    )


class FileProcessingTaskUpdate(SQLModel):
    """更新文件处理任务模型"""

    status: Optional[ProcessingStatus] = Field(default=None)
    progress: Optional[int] = Field(default=None, ge=0, le=100)
    error_message: Optional[str] = Field(default=None)
    result_data: Optional[dict] = Field(default=None, sa_type=JSON)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)


class FileProcessingTask(FileProcessingTaskBase, table=True):
    """文件处理任务表模型"""

    __tablename__ = "file_processing_tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="file_messages.id", description="关联的文件消息ID"
    )
    image_message_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="image_messages.id", description="关联的图片消息ID"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="创建时间"
    )


class FileProcessingTaskPublic(FileProcessingTaskBase):
    """文件处理任务公开模型"""

    id: uuid.UUID
    file_message_id: Optional[uuid.UUID]
    image_message_id: Optional[uuid.UUID]
    created_at: datetime


# 响应模型
class ImageMessageListResponse(SQLModel):
    """图片消息列表响应模型"""

    images: List[ImageMessagePublic]
    total: int
    skip: int
    limit: int


class FileMessageListResponse(SQLModel):
    """文件消息列表响应模型"""

    files: List[FileMessagePublic]
    total: int
    skip: int
    limit: int


class FileProcessingTaskListResponse(SQLModel):
    """文件处理任务列表响应模型"""

    tasks: List[FileProcessingTaskPublic]
    total: int
    skip: int
    limit: int


# 上传请求模型
class ImageUploadRequest(SQLModel):
    """图片上传请求模型"""

    conversation_id: Optional[uuid.UUID] = Field(default=None, description="会话ID")
    compress: bool = Field(default=True, description="是否压缩")
    max_width: int = Field(default=1920, ge=1, le=4096, description="最大宽度")
    max_height: int = Field(default=1080, ge=1, le=4096, description="最大高度")
    quality: int = Field(default=85, ge=1, le=100, description="压缩质量")


class FileUploadRequest(SQLModel):
    """文件上传请求模型"""

    conversation_id: Optional[uuid.UUID] = Field(default=None, description="会话ID")
    scan_security: bool = Field(default=True, description="是否安全扫描")


# 处理请求模型
class ImageProcessRequest(SQLModel):
    """图片处理请求模型"""

    operations: List[dict] = Field(description="处理操作列表")


class ImageProcessOperation(SQLModel):
    """图片处理操作模型"""

    type: str = Field(description="操作类型")
    params: dict = Field(default_factory=dict, description="操作参数")
