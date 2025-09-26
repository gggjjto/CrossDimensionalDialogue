"""
任务相关的Pydantic Schema
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.task import TaskStatus, TaskStep, TaskType
from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    """创建任务请求"""

    task_type: TaskType
    conversation_id: Optional[uuid.UUID] = None
    input_data: Dict[str, Any] = Field(..., description="任务输入数据")
    priority: int = Field(default=0, ge=0, le=10, description="任务优先级，0-10")
    max_retries: int = Field(default=3, ge=0, le=10, description="最大重试次数")
    task_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="任务元数据"
    )


class TaskResponse(BaseModel):
    """任务响应"""

    id: str = Field(..., description="任务ID")
    task_type: TaskType = Field(..., description="任务类型")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(..., ge=0, le=100, description="任务进度百分比")
    created_at: datetime = Field(..., description="创建时间")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    result: Optional[Dict[str, Any]] = Field(None, description="任务结果")
    error: Optional[str] = Field(None, description="错误信息")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="任务步骤")
    retry_count: int = Field(..., description="重试次数")
    max_retries: int = Field(..., description="最大重试次数")
    priority: int = Field(..., description="任务优先级")
    task_metadata: Dict[str, Any] = Field(
        default_factory=dict, description="任务元数据"
    )

    class Config:
        from_attributes = True


class TaskStatusResponse(BaseModel):
    """任务状态响应"""

    id: str
    status: TaskStatus
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class TaskStatusUpdate(BaseModel):
    """任务状态更新"""

    status: TaskStatus
    progress: Optional[int] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    step_name: Optional[str] = None
    step_result: Optional[Dict[str, Any]] = None


class TaskListRequest(BaseModel):
    """任务列表查询请求"""

    task_type: Optional[TaskType] = None
    status: Optional[TaskStatus] = None
    conversation_id: Optional[uuid.UUID] = None
    skip: int = Field(default=0, ge=0, description="跳过的记录数")
    limit: int = Field(default=20, ge=1, le=100, description="返回的记录数")
    order_by: str = Field(default="created_at", description="排序字段")
    order: str = Field(default="desc", description="排序方向")


class TaskListResponse(BaseModel):
    """任务列表响应"""

    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int


class TaskCancelRequest(BaseModel):
    """取消任务请求"""

    reason: Optional[str] = Field(None, description="取消原因")


class TaskStatsResponse(BaseModel):
    """任务统计响应"""

    total_tasks: int
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    success_rate: float
    average_processing_time: Optional[float] = None


class VoiceMessageTaskInput(BaseModel):
    """语音消息任务输入"""

    audio_url: str = Field(..., description="音频文件URL")
    voice_preference: Optional[str] = Field(None, description="音色偏好")
    enable_tts: bool = Field(default=True, description="是否启用TTS")


class TextMessageTaskInput(BaseModel):
    """文本消息任务输入"""

    message: str = Field(..., description="消息内容")
    enable_tts: bool = Field(default=True, description="是否启用TTS")


class TTSGenerationTaskInput(BaseModel):
    """TTS生成任务输入"""

    text: str = Field(..., description="要转换的文本")
    voice: str = Field(default="Cherry", description="音色")
    audio_format: str = Field(default="wav", description="音频格式")
    sample_rate: int = Field(default=24000, description="采样率")


class STTTranscriptionTaskInput(BaseModel):
    """STT转录任务输入"""

    audio_url: str = Field(..., description="音频文件URL")
    model: Optional[str] = Field(None, description="STT模型")
    prompt: Optional[str] = Field(None, description="提示词")
    response_format: str = Field(default="json", description="响应格式")
    temperature: Optional[float] = Field(None, description="温度参数")
