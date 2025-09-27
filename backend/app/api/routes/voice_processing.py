"""
语音处理API路由
包括TTS（文本转语音）和STT（语音转文本）功能
"""

import logging
import uuid
from typing import Optional

from app.api.deps import get_current_active_superuser, get_current_user, get_db
from app.models.user import User
from app.schemas.task import (
    STTTranscriptionTaskInput,
    TaskCreateRequest,
    TaskResponse,
    TaskType,
    TTSGenerationTaskInput,
    VoiceMessageTaskInput,
)
from app.schemas.voice_message import (
    VoiceMessageRequest,
    VoiceMessageResponse,
    VoiceUploadResponse,
)
from app.services.dialogue_orchestration_service import dialogue_orchestration_service
from app.services.qiniu_storage_service import qiniu_storage_service
from app.services.stt_service import STTRequest, stt_service
from app.services.task_queue_service import task_queue_service
from app.services.tts_service import TTSRequest, tts_service
from app.services.voice_catalog_service import list_voices
from app.services.voice_demo_service import voice_demo_service
from app.utils.response import error_response, success_response
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlmodel import Session

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
        import os
        import tempfile
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


@router.post("/message", status_code=status.HTTP_202_ACCEPTED)
async def process_voice_message(
    *,
    db: Session = Depends(get_db),
    request: VoiceMessageRequest,
    current_user: User = Depends(get_current_user),
):
    """
    处理语音消息 - 异步任务版本

    完整的语音对话流程：
    1. STT: 语音转文本
    2. LLM: AI生成回复
    3. TTS: 文本转语音
    4. 返回任务ID，通过轮询获取结果
    """
    try:
        # 验证音频URL
        if not request.audio_file_url or not request.audio_file_url.startswith("http"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="音频URL无效"
            )

        # 创建语音消息任务
        task_input = VoiceMessageTaskInput(
            audio_url=request.audio_file_url,
            voice_preference=request.voice_preference,
            enable_tts=True,
        )

        task_request = TaskCreateRequest(
            task_type=TaskType.VOICE_MESSAGE,
            conversation_id=request.conversation_id,
            input_data=task_input.dict(),
            priority=5,  # 中等优先级
            task_metadata={
                "user_id": str(current_user.id),
                "voice_preference": request.voice_preference,
            },
        )

        # 创建任务
        task = await task_queue_service.create_task(
            db=db, user_id=current_user.id, request=task_request
        )

        return success_response(
            data={
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
            },
            msg="语音消息处理任务已创建",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建语音消息处理任务失败: {str(e)}")
        return error_response(msg=f"创建语音消息处理任务失败: {str(e)}")


@router.post("/tts", status_code=status.HTTP_202_ACCEPTED)
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
    文本转语音 - 异步任务版本

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

        # 创建TTS生成任务
        task_input = TTSGenerationTaskInput(
            text=text, voice=voice, audio_format=audio_format, sample_rate=sample_rate
        )

        task_request = TaskCreateRequest(
            task_type=TaskType.TTS_GENERATION,
            input_data=task_input.dict(),
            priority=3,  # 较低优先级
            task_metadata={"user_id": str(current_user.id), "text_length": len(text)},
        )

        # 创建任务
        task = await task_queue_service.create_task(
            db=db, user_id=current_user.id, request=task_request
        )

        return success_response(
            data={
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
            },
            msg="TTS生成任务已创建",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建TTS生成任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建TTS生成任务失败",
        )


@router.post("/stt", status_code=status.HTTP_202_ACCEPTED)
async def speech_to_text(
    *,
    audio_url: str,
    model: Optional[str] = None,
    prompt: Optional[str] = None,
    response_format: str = "json",
    temperature: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    语音转文本 - 异步任务版本

    将语音文件转换为文本
    """
    try:
        if not audio_url or not audio_url.startswith("http"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="音频URL必须是公网可访问的HTTP链接",
            )

        # 创建STT转录任务
        task_input = STTTranscriptionTaskInput(
            audio_url=audio_url,
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )

        task_request = TaskCreateRequest(
            task_type=TaskType.STT_TRANSCRIPTION,
            input_data=task_input.dict(),
            priority=4,  # 中等优先级
            task_metadata={"user_id": str(current_user.id), "audio_url": audio_url},
        )

        # 创建任务
        task = await task_queue_service.create_task(
            db=db, user_id=current_user.id, request=task_request
        )

        return success_response(
            data={
                "task_id": task.id,
                "status": task.status,
                "progress": task.progress,
                "created_at": task.created_at,
            },
            msg="STT转录任务已创建",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建STT转录任务失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建STT转录任务失败",
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
