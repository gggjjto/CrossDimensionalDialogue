"""
任务相关的数据模型
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel
from sqlmodel import JSON, Field, SQLModel


class TaskStatus(str, Enum):
    """任务状态枚举"""

    PENDING = "PENDING"  # 等待处理
    PROCESSING = "PROCESSING"  # 正在处理
    COMPLETED = "COMPLETED"  # 处理完成
    FAILED = "FAILED"  # 处理失败
    CANCELLED = "CANCELLED"  # 用户取消
    TIMEOUT = "TIMEOUT"  # 处理超时


class TaskType(str, Enum):
    """任务类型枚举"""

    VOICE_MESSAGE = "VOICE_MESSAGE"  # 语音消息处理
    TEXT_MESSAGE = "TEXT_MESSAGE"  # 文本消息处理
    TTS_GENERATION = "TTS_GENERATION"  # 文本转语音
    STT_TRANSCRIPTION = "STT_TRANSCRIPTION"  # 语音转文本
    IMAGE_GENERATION = "IMAGE_GENERATION"  # 图像生成
    CHARACTER_GENERATION = "CHARACTER_GENERATION"  # 角色生成


class TaskStep(BaseModel):
    """任务步骤"""

    name: str  # 步骤名称
    status: TaskStatus  # 步骤状态
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    result: Optional[Dict[str, Any]] = None


class AITask(SQLModel, table=True):
    """AI任务数据模型"""

    __tablename__ = "ai_tasks"

    # 基本信息
    id: str = Field(primary_key=True, index=True)
    user_id: uuid.UUID = Field(index=True)
    conversation_id: Optional[uuid.UUID] = Field(default=None, index=True)

    # 任务信息
    task_type: TaskType = Field(index=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    progress: int = Field(default=0)

    # 输入数据
    input_data: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)

    # 处理步骤
    steps: List[Dict[str, Any]] = Field(default_factory=list, sa_type=JSON)

    # 结果数据
    result: Optional[Dict[str, Any]] = Field(default=None, sa_type=JSON)
    error: Optional[str] = Field(default=None)

    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)

    # 重试信息
    retry_count: int = Field(default=0)
    max_retries: int = Field(default=3)

    # RQ任务ID
    rq_job_id: Optional[str] = Field(default=None, index=True)

    # 优先级
    priority: int = Field(default=0)  # 数字越大优先级越高

    # 元数据
    task_metadata: Dict[str, Any] = Field(default_factory=dict, sa_type=JSON)


class TaskCreate(BaseModel):
    """创建任务请求"""

    task_type: TaskType
    conversation_id: Optional[uuid.UUID] = None
    input_data: Dict[str, Any]
    priority: int = 0
    max_retries: int = 3
    task_metadata: Dict[str, Any] = {}


class TaskResponse(BaseModel):
    """任务响应"""

    id: str
    task_type: TaskType
    status: TaskStatus
    progress: int
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    steps: List[Dict[str, Any]] = []
    retry_count: int
    max_retries: int
    priority: int
    task_metadata: Dict[str, Any] = {}


class TaskListResponse(BaseModel):
    """任务列表响应"""

    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int


class TaskStats(BaseModel):
    """任务统计"""

    total_tasks: int
    pending_tasks: int
    processing_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    success_rate: float
    average_processing_time: Optional[float] = None
