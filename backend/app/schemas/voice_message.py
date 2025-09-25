"""
语音消息相关的Pydantic模式
"""

import uuid
from typing import Optional
from pydantic import BaseModel, Field


class VoiceMessageRequest(BaseModel):
    """语音消息请求"""

    conversation_id: uuid.UUID = Field(..., description="会话ID")
    audio_file_url: str = Field(..., description="音频文件的公网URL")
    voice_preference: Optional[str] = Field(None, description="偏好的音色")


class VoiceMessageResponse(BaseModel):
    """语音消息响应"""

    success: bool = Field(..., description="是否成功")
    user_message_id: Optional[uuid.UUID] = Field(None, description="用户消息ID")
    character_message_id: Optional[uuid.UUID] = Field(None, description="角色消息ID")
    text_response: Optional[str] = Field(None, description="文本回复")
    audio_response_url: Optional[str] = Field(None, description="语音回复URL")
    voice_used: Optional[str] = Field(None, description="使用的音色")
    stt_text: Optional[str] = Field(None, description="语音识别的文本")
    error: Optional[str] = Field(None, description="错误信息")


class VoiceUploadResponse(BaseModel):
    """语音文件上传响应"""

    success: bool = Field(..., description="是否成功")
    audio_url: Optional[str] = Field(None, description="音频文件URL")
    filename: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小")
    error: Optional[str] = Field(None, description="错误信息")
