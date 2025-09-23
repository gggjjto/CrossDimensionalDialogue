import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
)
from fastapi.responses import FileResponse
from sqlmodel import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.voice import (
    VoiceMessage,
    VoiceMessageCreate,
    VoiceMessagePublic,
    VoiceMessageListResponse,
    VoiceConfig,
    VoiceConfigCreate,
    VoiceConfigUpdate,
    VoiceConfigPublic,
    VoiceConfigListResponse,
    AudioProcessingTask,
    AudioProcessingTaskCreate,
    AudioProcessingTaskPublic,
    AudioProcessingTaskListResponse,
    VoiceSynthesisRequest,
    VoiceSynthesisResult,
    SpeechRecognitionResult,
    AudioQualityReport,
    VoiceMessageStats,
    AudioFormat,
    AudioQuality,
    VoiceLanguage,
    VoiceGender,
    VoiceEmotion,
    AudioProcessingStatus,
)
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.audio_storage_service import audio_storage_service
from app.crud import voice as voice_crud


router = APIRouter()


# 语音消息管理
@router.post(
    "/messages/", response_model=VoiceMessagePublic, status_code=status.HTTP_201_CREATED
)
async def create_voice_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    voice_message: VoiceMessageCreate,
) -> VoiceMessagePublic:
    """创建语音消息"""
    try:
        # 验证消息是否存在
        from app.crud import message as message_crud

        message = message_crud.get(db, id=voice_message.message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="关联的消息不存在"
            )

        # 验证用户权限
        if message.conversation.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问此消息"
            )

        # 创建语音消息
        db_voice_message = voice_crud.create(db, obj_in=voice_message)

        return db_voice_message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建语音消息失败: {str(e)}",
        )


@router.get("/messages/", response_model=VoiceMessageListResponse)
async def get_voice_messages(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    conversation_id: Optional[uuid.UUID] = None,
    voice_type: Optional[str] = None,
    language: Optional[VoiceLanguage] = None,
    status: Optional[AudioProcessingStatus] = None,
) -> VoiceMessageListResponse:
    """获取语音消息列表"""
    try:
        # 构建查询参数
        filters = {}
        if conversation_id:
            filters["conversation_id"] = conversation_id
        if voice_type:
            filters["voice_type"] = voice_type
        if language:
            filters["language"] = language
        if status:
            filters["processing_status"] = status

        # 获取语音消息
        voice_messages, total = voice_crud.get_multi(
            db, skip=skip, limit=limit, filters=filters, user_id=current_user.id
        )

        return VoiceMessageListResponse(
            voice_messages=voice_messages, total=total, skip=skip, limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音消息失败: {str(e)}",
        )


@router.get("/messages/{voice_message_id}", response_model=VoiceMessagePublic)
async def get_voice_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    voice_message_id: uuid.UUID,
) -> VoiceMessagePublic:
    """获取语音消息详情"""
    try:
        voice_message = voice_crud.get_by_user(
            db, id=voice_message_id, user_id=current_user.id
        )
        if not voice_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="语音消息不存在"
            )

        return voice_message

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音消息失败: {str(e)}",
        )


@router.delete("/messages/{voice_message_id}")
async def delete_voice_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    voice_message_id: uuid.UUID,
):
    """删除语音消息"""
    try:
        voice_message = voice_crud.get_by_user(
            db, id=voice_message_id, user_id=current_user.id
        )
        if not voice_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="语音消息不存在"
            )

        # 删除音频文件
        if voice_message.audio_url:
            await audio_storage_service.delete_file(voice_message.audio_url)

        # 删除数据库记录
        voice_crud.delete(db, id=voice_message_id)

        return {"message": "语音消息删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除语音消息失败: {str(e)}",
        )


# 语音文件上传和处理
@router.post("/upload/", response_model=Dict[str, Any])
async def upload_audio_file(
    *,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    conversation_id: Optional[uuid.UUID] = Form(None),
    language: VoiceLanguage = Form(VoiceLanguage.ZH_CN),
    enable_auto_detection: bool = Form(False),
) -> Dict[str, Any]:
    """上传音频文件"""
    try:
        # 验证文件
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件必须是音频格式"
            )

        # 读取文件内容
        file_content = await file.read()

        # 保存文件
        file_info = await audio_storage_service.save_uploaded_file(
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type,
            user_id=current_user.id,
            conversation_id=conversation_id,
        )

        # 异步处理音频文件
        background_tasks.add_task(
            process_uploaded_audio,
            file_info["file_id"],
            language,
            enable_auto_detection,
        )

        return {
            "file_id": file_info["file_id"],
            "filename": file_info["original_filename"],
            "file_size": file_info["file_size"],
            "audio_format": file_info["audio_format"],
            "status": "uploaded",
            "message": "文件上传成功，正在处理中...",
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传音频文件失败: {str(e)}",
        )


@router.get("/download/{file_id}")
async def download_audio_file(
    *, current_user: User = Depends(get_current_user), file_id: str
):
    """下载音频文件"""
    try:
        file_info = await audio_storage_service.get_file(file_id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在"
            )

        # 验证用户权限（这里需要根据实际需求实现）
        # 暂时跳过权限检查

        return FileResponse(
            path=file_info["storage_path"],
            filename=file_info["original_filename"],
            media_type="audio/mpeg",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"下载音频文件失败: {str(e)}",
        )


# 语音识别
@router.post("/transcribe/", response_model=SpeechRecognitionResult)
async def transcribe_audio(
    *,
    current_user: User = Depends(get_current_user),
    file_id: str = Form(...),
    language: VoiceLanguage = Form(VoiceLanguage.ZH_CN),
    enable_auto_detection: bool = Form(False),
    enable_punctuation: bool = Form(True),
    enable_word_timestamps: bool = Form(False),
) -> SpeechRecognitionResult:
    """语音转文本"""
    try:
        # 获取文件
        file_info = await audio_storage_service.get_file(file_id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="音频文件不存在"
            )

        # 执行语音识别
        result = await stt_service.transcribe_audio(
            audio_file_path=file_info["storage_path"],
            language=language,
            enable_auto_detection=enable_auto_detection,
            enable_punctuation=enable_punctuation,
            enable_word_timestamps=enable_word_timestamps,
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音识别失败: {str(e)}",
        )


# 语音合成
@router.post("/synthesize/", response_model=VoiceSynthesisResult)
async def synthesize_speech(
    *, current_user: User = Depends(get_current_user), request: VoiceSynthesisRequest
) -> VoiceSynthesisResult:
    """文本转语音"""
    try:
        # 执行语音合成
        result = await tts_service.synthesize_speech(request)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"语音合成失败: {str(e)}",
        )


# 语音配置管理
@router.post(
    "/configs/", response_model=VoiceConfigPublic, status_code=status.HTTP_201_CREATED
)
async def create_voice_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    voice_config: VoiceConfigCreate,
) -> VoiceConfigPublic:
    """创建语音配置"""
    try:
        # 验证角色是否存在
        from app.crud import character as character_crud

        character = character_crud.get(db, id=voice_config.character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在"
            )

        # 创建语音配置
        db_voice_config = voice_crud.create_voice_config(db, obj_in=voice_config)

        return db_voice_config

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建语音配置失败: {str(e)}",
        )


@router.get("/configs/", response_model=VoiceConfigListResponse)
async def get_voice_configs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    character_id: Optional[uuid.UUID] = None,
    is_active: Optional[bool] = None,
) -> VoiceConfigListResponse:
    """获取语音配置列表"""
    try:
        # 构建查询参数
        filters = {}
        if character_id:
            filters["character_id"] = character_id
        if is_active is not None:
            filters["is_active"] = is_active

        # 获取语音配置
        voice_configs, total = voice_crud.get_voice_configs(
            db, skip=skip, limit=limit, filters=filters
        )

        return VoiceConfigListResponse(
            voice_configs=voice_configs, total=total, skip=skip, limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音配置失败: {str(e)}",
        )


@router.get("/configs/{config_id}", response_model=VoiceConfigPublic)
async def get_voice_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    config_id: uuid.UUID,
) -> VoiceConfigPublic:
    """获取语音配置详情"""
    try:
        voice_config = voice_crud.get_voice_config(db, id=config_id)
        if not voice_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="语音配置不存在"
            )

        return voice_config

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音配置失败: {str(e)}",
        )


@router.put("/configs/{config_id}", response_model=VoiceConfigPublic)
async def update_voice_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    config_id: uuid.UUID,
    voice_config_update: VoiceConfigUpdate,
) -> VoiceConfigPublic:
    """更新语音配置"""
    try:
        voice_config = voice_crud.get_voice_config(db, id=config_id)
        if not voice_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="语音配置不存在"
            )

        # 更新语音配置
        updated_config = voice_crud.update_voice_config(
            db, db_obj=voice_config, obj_in=voice_config_update
        )

        return updated_config

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新语音配置失败: {str(e)}",
        )


@router.delete("/configs/{config_id}")
async def delete_voice_config(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    config_id: uuid.UUID,
):
    """删除语音配置"""
    try:
        voice_config = voice_crud.get_voice_config(db, id=config_id)
        if not voice_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="语音配置不存在"
            )

        # 删除语音配置
        voice_crud.delete_voice_config(db, id=config_id)

        return {"message": "语音配置删除成功"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除语音配置失败: {str(e)}",
        )


# 音频处理任务管理
@router.get("/tasks/", response_model=AudioProcessingTaskListResponse)
async def get_processing_tasks(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20,
    status: Optional[AudioProcessingStatus] = None,
) -> AudioProcessingTaskListResponse:
    """获取音频处理任务列表"""
    try:
        # 构建查询参数
        filters = {}
        if status:
            filters["status"] = status

        # 获取处理任务
        tasks, total = voice_crud.get_processing_tasks(
            db, skip=skip, limit=limit, filters=filters, user_id=current_user.id
        )

        return AudioProcessingTaskListResponse(
            tasks=tasks, total=total, skip=skip, limit=limit
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取处理任务失败: {str(e)}",
        )


@router.get("/tasks/{task_id}", response_model=AudioProcessingTaskPublic)
async def get_processing_task(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: uuid.UUID,
) -> AudioProcessingTaskPublic:
    """获取音频处理任务详情"""
    try:
        task = voice_crud.get_processing_task(db, id=task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="处理任务不存在"
            )

        return task

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取处理任务失败: {str(e)}",
        )


# 语音统计
@router.get("/stats/", response_model=VoiceMessageStats)
async def get_voice_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: Optional[uuid.UUID] = None,
) -> VoiceMessageStats:
    """获取语音消息统计"""
    try:
        stats = voice_crud.get_voice_stats(
            db, user_id=current_user.id, conversation_id=conversation_id
        )
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音统计失败: {str(e)}",
        )


# 音频质量检测
@router.post("/quality-check/", response_model=AudioQualityReport)
async def check_audio_quality(
    *, current_user: User = Depends(get_current_user), file_id: str = Form(...)
) -> AudioQualityReport:
    """检测音频质量"""
    try:
        # 获取文件
        file_info = await audio_storage_service.get_file(file_id)
        if not file_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="音频文件不存在"
            )

        # 检测音频质量
        quality_info = await stt_service.validate_audio_quality(
            file_info["storage_path"]
        )

        # 构建质量报告
        report = AudioQualityReport(
            overall_score=quality_info["quality_score"],
            clarity_score=quality_info["quality_score"] * 0.4,
            volume_score=quality_info["quality_score"] * 0.3,
            noise_level=quality_info["zero_crossing_rate"] * 10,
            sample_rate=quality_info["sample_rate"],
            bit_depth=16,  # 默认值
            channels=1,
            duration=quality_info["duration"],
            file_size=file_info["file_size"],
            format=file_info["audio_format"],
            issues=quality_info["issues"],
            recommendations=_generate_recommendations(quality_info),
        )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"音频质量检测失败: {str(e)}",
        )


# 获取可用语音列表
@router.get("/voices/")
async def get_available_voices(
    *,
    current_user: User = Depends(get_current_user),
    language: VoiceLanguage = VoiceLanguage.ZH_CN,
) -> List[Dict[str, Any]]:
    """获取可用的语音列表"""
    try:
        voices = await tts_service.get_available_voices(language)
        return voices

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取语音列表失败: {str(e)}",
        )


# 辅助函数
async def process_uploaded_audio(
    file_id: str, language: VoiceLanguage, enable_auto_detection: bool
) -> None:
    """处理上传的音频文件（后台任务）"""
    try:
        # 这里可以实现音频处理逻辑
        # 例如：语音识别、质量检测等
        pass

    except Exception as e:
        print(f"处理音频文件失败: {e}")


def _generate_recommendations(quality_info: Dict[str, Any]) -> List[str]:
    """生成音频质量改进建议"""
    recommendations = []

    if quality_info["rms"] < 0.01:
        recommendations.append("建议增加录音音量")
    elif quality_info["rms"] > 0.5:
        recommendations.append("建议降低录音音量")

    if quality_info["duration"] < 0.5:
        recommendations.append("建议录制更长的音频")
    elif quality_info["duration"] > 300:
        recommendations.append("建议分段录制音频")

    if quality_info["sample_rate"] < 16000:
        recommendations.append("建议使用更高的采样率录制")

    if quality_info["zero_crossing_rate"] > 0.1:
        recommendations.append("建议在安静的环境中录制")

    return recommendations
