"""
语音处理API路由
包括TTS（文本转语音）和STT（语音转文本）功能
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.services.tts_service import tts_service, TTSRequest
from app.services.stt_service import stt_service, STTRequest
from app.services.voice_catalog_service import list_voices
from app.services.dialogue_orchestration_service import dialogue_orchestration_service
from app.services.qiniu_storage_service import qiniu_storage_service
from app.schemas.voice_message import (
    VoiceMessageRequest,
    VoiceMessageResponse,
    VoiceUploadResponse,
)
from app.utils.response import success_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])


@router.get("/voices")
async def get_available_voices(
    *,
    db: Session = Depends(get_db),
    provider: str = "qwen3-tts",
    current_user: User = Depends(get_current_user),
):
    """
    获取可用的音色列表
    """
    try:
        voices = list_voices(db, provider=provider)

        voice_list = []
        for voice in voices:
            voice_list.append(
                {
                    "voice": voice.voice,
                    "name": voice.name,
                    "description": voice.description,
                    "preview_url": voice.preview_url,
                    "is_active": voice.is_active,
                }
            )

        return success_response(
            data={
                "voices": voice_list,
                "provider": provider,
                "total": len(voice_list),
            },
            message="获取音色列表成功",
        )

    except Exception as e:
        logger.error(f"获取音色列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取音色列表失败"
        )


@router.post("/upload-audio")
async def upload_audio_file(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    上传音频文件到云存储

    前端上传语音文件，返回公网可访问的URL
    """
    try:
        # 检查文件类型
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只支持音频文件"
            )

        # 检查文件大小（限制为10MB）
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过10MB"
            )

        # 创建临时文件
        import tempfile
        import os
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_{current_user.id}_{timestamp}.wav"

        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name

        try:
            # 上传到云存储
            upload_result = qiniu_storage_service.upload_audio_file(
                file_path=temp_file_path,
                user_id=str(current_user.id),
                file_type="voice_message",
            )

            return success_response(
                data={
                    "success": True,
                    "audio_url": upload_result.get("url", ""),
                    "filename": filename,
                    "file_size": len(file_content),
                },
                msg="音频文件上传成功",
            )

        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传音频文件失败: {str(e)}")
        return error_response(msg=f"上传音频文件失败: {str(e)}")


@router.post("/message")
async def process_voice_message(
    *,
    db: Session = Depends(get_db),
    request: VoiceMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """
    处理语音消息

    完整的语音对话流程：
    1. STT: 语音转文本
    2. LLM: AI生成回复
    3. TTS: 文本转语音
    4. 返回文本回复和语音回复URL
    """
    try:
        # 验证音频URL
        if not request.audio_file_url or not request.audio_file_url.startswith("http"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="音频URL无效"
            )

        # 调用对话编排服务处理语音消息
        result = await dialogue_orchestration_service.process_voice_message(
            db=db,
            conversation_id=request.conversation_id,
            audio_url=request.audio_file_url,
            user_id=current_user.id,
            settings=None,  # 使用默认设置
            voice_preference=request.voice_preference,
        )

        if result["success"]:
            return success_response(
                data={
                    "success": True,
                    "user_message_id": (
                        result["user_message"].id if result["user_message"] else None
                    ),
                    "character_message_id": (
                        result["character_message"].id
                        if result["character_message"]
                        else None
                    ),
                    "text_response": result["text_response"],
                    "audio_response_url": result["audio_response_url"],
                    "voice_used": result["voice_used"],
                    "stt_text": result["stt_text"],
                },
                msg="语音消息处理成功",
            )
        else:
            return error_response(msg=result["error"])

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理语音消息失败: {str(e)}")
        return error_response(msg=f"处理语音消息失败: {str(e)}")


@router.post("/tts")
async def text_to_speech(
    *,
    db: Session = Depends(get_db),
    text: str,
    voice: Optional[str] = None,
    audio_format: str = "wav",
    sample_rate: int = 24000,
    current_user: User = Depends(get_current_user),
):
    """
    文本转语音

    将文本转换为语音文件
    """
    try:
        if not text or not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文本内容不能为空"
            )

        if len(text) > 600:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="文本长度不能超过600字符",
            )

        # 如果没有指定音色，使用默认音色Cherry
        if not voice:
            voice = "Cherry"  # 默认音色

        # 创建TTS请求
        tts_request = TTSRequest(
            text=text,
            voice=voice,
            audio_format=audio_format,
            sample_rate=sample_rate,
        )

        # 调用TTS服务
        tts_response = await tts_service.synthesize(tts_request)

        if not tts_response.audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="语音生成失败"
            )

        # 返回音频数据
        import base64

        audio_base64 = base64.b64encode(tts_response.audio_bytes).decode("utf-8")

        return success_response(
            data={
                "audio_data": audio_base64,
                "content_type": tts_response.content_type,
                "voice": voice,
                "duration_sec": tts_response.duration_sec,
                "model": tts_response.model,
            },
            message="语音生成成功",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文本转语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="文本转语音失败"
        )


@router.post("/stt")
async def speech_to_text(
    *,
    audio_url: str,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    response_format: str = "json",
    temperature: Optional[float] = None,
    current_user: User = Depends(get_current_user),
):
    """
    语音转文本

    将语音文件转换为文本
    """
    try:
        if not audio_url or not audio_url.startswith("http"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频URL必须是公网可访问的HTTP链接",
            )

        # 创建STT请求
        stt_request = STTRequest(
            audio_url=audio_url,
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )

        # 调用STT服务
        stt_response = await stt_service.transcribe(stt_request)

        return success_response(
            data={
                "text": stt_response.text,
                "language": stt_response.language,
                "duration_sec": stt_response.duration_sec,
                "model": stt_response.model,
                "words": stt_response.words,
            },
            message="语音识别成功",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"语音转文本失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="语音转文本失败"
        )


@router.post("/generate-all")
async def generate_all_voice_demos(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    provider: str = Query("qwen3-tts", description="音色提供方"),
    force_regenerate: bool = Query(False, description="是否强制重新生成"),
):
    """
    为所有音色生成示例语音

    需要超级用户权限
    """
    try:
        result = await voice_demo_service.generate_demo_audio_for_all_voices(
            session=db, provider=provider, force_regenerate=force_regenerate
        )

        if result["success"]:
            return success_response(
                data=result,
                msg=f"音色示例语音生成完成: 成功 {result['success_count']}, 失败 {result['failed_count']}, 跳过 {result['skipped_count']}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "生成失败"),
            )

    except Exception as e:
        logger.error(f"生成音色示例语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成音色示例语音失败: {str(e)}",
        )
