import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)
from sqlmodel import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.websocket import (
    WebSocketMessageType,
    VoiceMessageData,
    VoiceUploadProgressData,
    VoiceProcessingProgressData,
    VoiceSynthesisProgressData,
    VoiceQualityCheckData,
    VoiceErrorData,
)
from app.services.websocket_manager import websocket_manager
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.audio_storage_service import audio_storage_service
from app.crud import voice as voice_crud
from app.models.voice import (
    VoiceMessageCreate,
    VoiceMessageType as VoiceMsgType,
    AudioFormat,
    VoiceLanguage,
    AudioProcessingStatus,
)

router = APIRouter()


@router.websocket("/voice/{conversation_id}")
async def voice_websocket_endpoint(
    websocket: WebSocket,
    conversation_id: str,
    token: Optional[str] = None,
):
    """语音消息WebSocket端点"""
    try:
        # 验证用户身份
        if not token:
            await websocket.close(code=4001, reason="Missing authentication token")
            return

        # 这里应该验证token并获取用户信息
        # 为了简化，我们假设token验证通过
        user_id = uuid.uuid4()  # 实际应用中应该从token解析

        # 建立WebSocket连接
        connection_id = await websocket_manager.connect(
            websocket, user_id, uuid.UUID(conversation_id)
        )

        print(f"语音WebSocket连接建立: {connection_id}")

        try:
            while True:
                # 接收消息
                data = await websocket.receive_text()
                message = json.loads(data)

                # 处理不同类型的消息
                await handle_voice_message(websocket, connection_id, message)

        except WebSocketDisconnect:
            print(f"语音WebSocket连接断开: {connection_id}")
        finally:
            await websocket_manager.disconnect(connection_id)

    except Exception as e:
        print(f"语音WebSocket错误: {e}")
        try:
            await websocket.close(code=4000, reason="Internal server error")
        except:
            pass


async def handle_voice_message(
    websocket: WebSocket, connection_id: str, message: Dict[str, Any]
):
    """处理语音消息"""
    try:
        message_type = message.get("type")
        data = message.get("data", {})

        if message_type == "voice_upload_start":
            await handle_voice_upload_start(websocket, connection_id, data)
        elif message_type == "voice_upload_progress":
            await handle_voice_upload_progress(websocket, connection_id, data)
        elif message_type == "voice_processing_start":
            await handle_voice_processing_start(websocket, connection_id, data)
        elif message_type == "voice_processing_progress":
            await handle_voice_processing_progress(websocket, connection_id, data)
        elif message_type == "voice_synthesis_start":
            await handle_voice_synthesis_start(websocket, connection_id, data)
        elif message_type == "voice_synthesis_progress":
            await handle_voice_synthesis_progress(websocket, connection_id, data)
        elif message_type == "voice_quality_check":
            await handle_voice_quality_check(websocket, connection_id, data)
        else:
            await send_error_message(
                websocket, "unknown_message_type", f"未知的消息类型: {message_type}"
            )

    except Exception as e:
        print(f"处理语音消息失败: {e}")
        await send_error_message(websocket, "processing_error", str(e))


async def handle_voice_upload_start(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音上传开始"""
    try:
        file_id = data.get("file_id")
        filename = data.get("filename")
        file_size = data.get("file_size")

        if not file_id or not filename:
            await send_error_message(websocket, "invalid_data", "缺少必要的文件信息")
            return

        # 发送上传开始确认
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_UPLOAD_START,
            {
                "file_id": file_id,
                "filename": filename,
                "file_size": file_size,
                "status": "started",
                "message": "开始上传语音文件",
            },
        )

        # 模拟上传进度
        await simulate_upload_progress(websocket, file_id, file_size)

    except Exception as e:
        await send_error_message(websocket, "upload_start_error", str(e))


async def handle_voice_upload_progress(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音上传进度"""
    try:
        file_id = data.get("file_id")
        progress = data.get("progress", 0)
        bytes_uploaded = data.get("bytes_uploaded", 0)
        total_bytes = data.get("total_bytes", 0)

        # 发送进度更新
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_UPLOAD_PROGRESS,
            VoiceUploadProgressData(
                file_id=file_id,
                progress=progress,
                bytes_uploaded=bytes_uploaded,
                total_bytes=total_bytes,
                estimated_time_remaining=max(0, int((100 - progress) * 2)),  # 简单估算
            ).model_dump(),
        )

    except Exception as e:
        await send_error_message(websocket, "upload_progress_error", str(e))


async def handle_voice_processing_start(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音处理开始"""
    try:
        file_id = data.get("file_id")
        processing_type = data.get("processing_type", "transcription")

        if not file_id:
            await send_error_message(websocket, "invalid_data", "缺少文件ID")
            return

        # 创建处理任务
        task_id = uuid.uuid4()

        # 发送处理开始确认
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_PROCESSING_START,
            {
                "task_id": str(task_id),
                "file_id": file_id,
                "processing_type": processing_type,
                "status": "started",
                "message": "开始处理语音文件",
            },
        )

        # 异步处理语音
        asyncio.create_task(
            process_voice_async(websocket, task_id, file_id, processing_type)
        )

    except Exception as e:
        await send_error_message(websocket, "processing_start_error", str(e))


async def handle_voice_processing_progress(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音处理进度"""
    try:
        task_id = data.get("task_id")
        progress = data.get("progress", 0)
        status = data.get("status", "processing")

        # 发送进度更新
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_PROCESSING_PROGRESS,
            VoiceProcessingProgressData(
                task_id=uuid.UUID(task_id) if task_id else uuid.uuid4(),
                file_id=data.get("file_id", ""),
                processing_type=data.get("processing_type", "transcription"),
                progress=progress,
                status=status,
                estimated_time_remaining=max(0, int((100 - progress) * 3)),  # 简单估算
            ).model_dump(),
        )

    except Exception as e:
        await send_error_message(websocket, "processing_progress_error", str(e))


async def handle_voice_synthesis_start(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音合成开始"""
    try:
        text = data.get("text")
        voice_config_id = data.get("voice_config_id")

        if not text:
            await send_error_message(websocket, "invalid_data", "缺少合成文本")
            return

        synthesis_id = str(uuid.uuid4())

        # 发送合成开始确认
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_SYNTHESIS_START,
            {
                "synthesis_id": synthesis_id,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "status": "started",
                "message": "开始语音合成",
            },
        )

        # 异步进行语音合成
        asyncio.create_task(
            synthesize_voice_async(websocket, synthesis_id, text, voice_config_id)
        )

    except Exception as e:
        await send_error_message(websocket, "synthesis_start_error", str(e))


async def handle_voice_synthesis_progress(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音合成进度"""
    try:
        synthesis_id = data.get("synthesis_id")
        progress = data.get("progress", 0)
        status = data.get("status", "synthesizing")

        # 发送进度更新
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_SYNTHESIS_PROGRESS,
            VoiceSynthesisProgressData(
                synthesis_id=synthesis_id or str(uuid.uuid4()),
                text=data.get("text", ""),
                progress=progress,
                status=status,
                estimated_time_remaining=max(0, int((100 - progress) * 2)),  # 简单估算
            ).model_dump(),
        )

    except Exception as e:
        await send_error_message(websocket, "synthesis_progress_error", str(e))


async def handle_voice_quality_check(
    websocket: WebSocket, connection_id: str, data: Dict[str, Any]
):
    """处理语音质量检测"""
    try:
        file_id = data.get("file_id")

        if not file_id:
            await send_error_message(websocket, "invalid_data", "缺少文件ID")
            return

        # 获取文件信息
        file_info = await audio_storage_service.get_file(file_id)
        if not file_info:
            await send_error_message(websocket, "file_not_found", "文件不存在")
            return

        # 检测音频质量
        quality_info = await stt_service.validate_audio_quality(
            file_info["storage_path"]
        )

        # 发送质量检测结果
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_QUALITY_CHECK,
            VoiceQualityCheckData(
                file_id=file_id,
                quality_score=quality_info.get("quality_score", 0.0),
                duration=quality_info.get("duration", 0.0),
                sample_rate=quality_info.get("sample_rate", 0),
                rms=quality_info.get("rms", 0.0),
                zero_crossing_rate=quality_info.get("zero_crossing_rate", 0.0),
                issues=quality_info.get("issues", []),
                recommendations=quality_info.get("recommendations", []),
                is_good_quality=quality_info.get("is_good_quality", False),
            ).model_dump(),
        )

    except Exception as e:
        await send_error_message(websocket, "quality_check_error", str(e))


async def simulate_upload_progress(
    websocket: WebSocket, file_id: str, total_bytes: int
):
    """模拟上传进度"""
    try:
        for progress in range(0, 101, 10):
            await send_voice_message(
                websocket,
                WebSocketMessageType.VOICE_UPLOAD_PROGRESS,
                VoiceUploadProgressData(
                    file_id=file_id,
                    progress=float(progress),
                    bytes_uploaded=int(total_bytes * progress / 100),
                    total_bytes=total_bytes,
                    estimated_time_remaining=max(0, (100 - progress) // 10),
                ).model_dump(),
            )
            await asyncio.sleep(0.5)  # 模拟上传延迟

        # 发送上传完成消息
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_UPLOAD_COMPLETE,
            {"file_id": file_id, "status": "completed", "message": "语音文件上传完成"},
        )

    except Exception as e:
        print(f"模拟上传进度失败: {e}")


async def process_voice_async(
    websocket: WebSocket, task_id: uuid.UUID, file_id: str, processing_type: str
):
    """异步处理语音"""
    try:
        # 获取文件信息
        file_info = await audio_storage_service.get_file(file_id)
        if not file_info:
            await send_error_message(websocket, "file_not_found", "文件不存在")
            return

        # 模拟处理进度
        for progress in range(0, 101, 20):
            await send_voice_message(
                websocket,
                WebSocketMessageType.VOICE_PROCESSING_PROGRESS,
                VoiceProcessingProgressData(
                    task_id=task_id,
                    file_id=file_id,
                    processing_type=processing_type,
                    progress=float(progress),
                    status="processing",
                    estimated_time_remaining=max(0, (100 - progress) // 20),
                ).model_dump(),
            )
            await asyncio.sleep(1)  # 模拟处理延迟

        # 执行实际的语音处理
        if processing_type == "transcription":
            result = await stt_service.transcribe_audio(
                file_info["storage_path"], language=VoiceLanguage.ZH_CN
            )

            # 发送处理完成消息
            await send_voice_message(
                websocket,
                WebSocketMessageType.VOICE_PROCESSING_COMPLETE,
                {
                    "task_id": str(task_id),
                    "file_id": file_id,
                    "processing_type": processing_type,
                    "status": "completed",
                    "result": {
                        "text": result.text,
                        "confidence": result.confidence,
                        "language": result.language.value,
                        "duration": result.duration,
                        "word_count": result.word_count,
                    },
                    "message": "语音处理完成",
                },
            )

    except Exception as e:
        await send_error_message(websocket, "processing_error", str(e))


async def synthesize_voice_async(
    websocket: WebSocket, synthesis_id: str, text: str, voice_config_id: Optional[str]
):
    """异步语音合成"""
    try:
        # 模拟合成进度
        for progress in range(0, 101, 25):
            await send_voice_message(
                websocket,
                WebSocketMessageType.VOICE_SYNTHESIS_PROGRESS,
                VoiceSynthesisProgressData(
                    synthesis_id=synthesis_id,
                    text=text[:50] + "..." if len(text) > 50 else text,
                    progress=float(progress),
                    status="synthesizing",
                    estimated_time_remaining=max(0, (100 - progress) // 25),
                ).model_dump(),
            )
            await asyncio.sleep(0.8)  # 模拟合成延迟

        # 执行实际的语音合成
        from app.models.voice import VoiceSynthesisRequest, AudioFormat, AudioQuality

        request = VoiceSynthesisRequest(
            text=text,
            voice_config_id=uuid.UUID(voice_config_id) if voice_config_id else None,
            output_format=AudioFormat.MP3,
            output_quality=AudioQuality.MEDIUM,
        )

        result = await tts_service.synthesize_speech(request)

        # 发送合成完成消息
        await send_voice_message(
            websocket,
            WebSocketMessageType.VOICE_SYNTHESIS_COMPLETE,
            {
                "synthesis_id": synthesis_id,
                "text": text,
                "status": "completed",
                "audio_url": result.audio_url,
                "duration": result.duration,
                "file_size": result.file_size,
                "format": result.format.value,
                "quality": result.quality.value,
                "message": "语音合成完成",
            },
        )

    except Exception as e:
        await send_error_message(websocket, "synthesis_error", str(e))


async def send_voice_message(
    websocket: WebSocket, message_type: WebSocketMessageType, data: Dict[str, Any]
):
    """发送语音消息"""
    try:
        message = {
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await websocket.send_text(json.dumps(message))
    except Exception as e:
        print(f"发送语音消息失败: {e}")


async def send_error_message(websocket: WebSocket, error_code: str, error_message: str):
    """发送错误消息"""
    try:
        error_data = VoiceErrorData(
            error_type="voice_processing",
            error_code=error_code,
            error_message=error_message,
            can_retry=error_code not in ["file_not_found", "invalid_data"],
        )

        await send_voice_message(
            websocket, WebSocketMessageType.VOICE_ERROR, error_data.model_dump()
        )
    except Exception as e:
        print(f"发送错误消息失败: {e}")


# 语音消息广播功能
async def broadcast_voice_message_to_conversation(
    conversation_id: uuid.UUID, voice_message_data: VoiceMessageData
):
    """向会话广播语音消息"""
    try:
        message = {
            "type": WebSocketMessageType.VOICE_MESSAGE.value,
            "data": voice_message_data.model_dump(),
            "timestamp": datetime.utcnow().isoformat(),
        }

        await websocket_manager.broadcast_to_conversation(conversation_id, message)
    except Exception as e:
        print(f"广播语音消息失败: {e}")


async def broadcast_voice_processing_update(
    conversation_id: uuid.UUID, task_id: uuid.UUID, status: str, progress: float = 0.0
):
    """广播语音处理状态更新"""
    try:
        message = {
            "type": WebSocketMessageType.VOICE_PROCESSING_PROGRESS.value,
            "data": {
                "task_id": str(task_id),
                "status": status,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat(),
            },
        }

        await websocket_manager.broadcast_to_conversation(conversation_id, message)
    except Exception as e:
        print(f"广播语音处理更新失败: {e}")
