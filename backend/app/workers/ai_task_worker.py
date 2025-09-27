"""
AI任务处理Worker - 简化版本
"""

import asyncio
import inspect
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from app.core.config import settings
from app.core.db import engine
from app.core.logger import get_logger
from app.crud.conversation import message as message_crud
from app.models.conversation import Message as ConversationMessage
from app.models.task import AITask, TaskStatus, TaskType
from app.schemas.task import (
    STTTranscriptionTaskInput,
    TextMessageTaskInput,
    TTSGenerationTaskInput,
    VoiceMessageTaskInput,
)
from app.services.dialogue_orchestration_service import dialogue_orchestration_service
from app.services.stt_service import STTRequest, stt_service
from app.services.tts_service import TTSRequest, tts_service
from sqlmodel import Session, select

logger = get_logger("ai_task_worker")


class AITaskWorker:
    """AI任务处理Worker"""

    def __init__(self):
        self.dialogue_service = dialogue_orchestration_service

    @staticmethod
    def _run_sync(value):
        """在同步环境执行可能的协程/可等待对象或直接返回结果。"""
        if inspect.isawaitable(value):
            return asyncio.run(value)
        return value

    @staticmethod
    def _run_sync_call(func, *args, **kwargs):
        """调用函数，若返回可等待对象则在同步环境执行。"""
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return asyncio.run(result)
        return result

    @staticmethod
    def _json_safe(value):
        """将对象转换为可JSON序列化的结构。"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, dict):
            return {k: AITaskWorker._json_safe(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [AITaskWorker._json_safe(v) for v in value]
        # 兜底：转换为字符串
        return str(value)

    def process_voice_message_task(self, task_id: str) -> Dict[str, Any]:
        """处理语音消息任务"""
        logger.info(f"开始处理语音消息任务: {task_id}")

        with Session(engine) as db:
            try:
                # 获取任务
                statement = select(AITask).where(AITask.id == task_id)
                task = db.exec(statement).first()

                if not task:
                    logger.error(f"任务不存在: {task_id}")
                    return {"success": False, "error": "任务不存在"}

                # 更新任务状态为处理中
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.utcnow()
                db.add(task)
                db.commit()

                # 解析输入数据
                input_data = VoiceMessageTaskInput(**task.input_data)

                # 步骤1: STT - 语音转文本
                logger.info(f"开始STT处理: {task_id}")
                task.progress = 10
                db.add(task)
                db.commit()

                stt_request = STTRequest(audio_url=input_data.audio_url)
                stt_response = self._run_sync_call(stt_service.transcribe, stt_request)

                if not stt_response.text:
                    raise ValueError("STT处理失败，无法获取文本内容")

                # 更新STT步骤完成
                task.progress = 33
                for step in task.steps:
                    if step.get("name") == "stt":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {"text": stt_response.text}
                        break
                db.add(task)
                db.commit()

                # 步骤2: LLM - 生成回复
                logger.info(f"开始LLM处理: {task_id}")
                task.progress = 40
                db.add(task)
                db.commit()

                # 调用对话编排服务生成回复
                llm_result = self._run_sync_call(
                    dialogue_orchestration_service.process_user_message,
                    db=db,
                    conversation_id=task.conversation_id,
                    user_message=stt_response.text,
                    user_id=task.user_id,
                    settings=None,
                )

                if not llm_result["success"]:
                    raise ValueError(f"LLM处理失败: {llm_result['error']}")

                # 将原始用户语音的audio_url写入用户消息记录
                try:
                    user_message_id = llm_result["user_message"].id
                    db_user_message: Optional[ConversationMessage] = message_crud.get(
                        db, id=user_message_id
                    )
                    if db_user_message:
                        db_user_message.audio_url = input_data.audio_url
                        duration_sec = getattr(stt_response, "duration_sec", None)
                        if duration_sec is not None:
                            try:
                                db_user_message.audio_duration = int(
                                    round(duration_sec)
                                )
                            except Exception:
                                pass
                        db_user_message.updated_at = datetime.utcnow()
                        db.add(db_user_message)
                        db.commit()
                except Exception:
                    # 不因写入失败而中断主流程
                    pass

                # 更新LLM步骤完成
                task.progress = 66
                for step in task.steps:
                    if step.get("name") == "llm":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {
                            "content": llm_result["character_response"].content
                        }
                        break
                db.add(task)
                db.commit()

                # 步骤3: TTS - 文本转语音
                audio_url = None
                voice_used = None

                if input_data.enable_tts and llm_result["character_response"].content:
                    logger.info(f"开始TTS处理: {task_id}")
                    task.progress = 70
                    db.add(task)
                    db.commit()

                    # 使用默认音色或用户偏好
                    voice = input_data.voice_preference or "Cherry"

                    tts_request = TTSRequest(
                        text=llm_result["character_response"].content,
                        voice=voice,
                        audio_format="wav",
                        sample_rate=24000,
                    )

                    tts_response = self._run_sync_call(
                        tts_service.synthesize, tts_request
                    )

                    if tts_response.audio_bytes:
                        # 保存音频文件到云存储
                        import os
                        import tempfile

                        from app.services.qiniu_storage_service import (
                            qiniu_storage_service,
                        )

                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".wav"
                        ) as temp_file:
                            temp_file.write(tts_response.audio_bytes)
                            temp_file_path = temp_file.name

                        try:
                            upload_result = qiniu_storage_service.upload_audio_file(
                                file_path=temp_file_path,
                                user_id=str(task.user_id),
                                conversation_id=str(task.conversation_id),
                                file_type="tts_audio",
                            )
                            audio_url = upload_result.get("url", "")
                            voice_used = voice
                        finally:
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)

                # 更新TTS步骤完成
                task.progress = 100
                for step in task.steps:
                    if step.get("name") == "tts":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {"audio_url": audio_url, "voice": voice_used}
                        break
                db.add(task)
                db.commit()

                # 将生成的TTS音频URL写入角色消息记录
                try:
                    character_message_id = llm_result["character_message"].id
                    db_character_message: Optional[ConversationMessage] = (
                        message_crud.get(db, id=character_message_id)
                    )
                    if db_character_message and audio_url:
                        db_character_message.audio_url = audio_url
                        db_character_message.updated_at = datetime.utcnow()
                        db.add(db_character_message)
                        db.commit()
                except Exception:
                    # 不因写入失败而中断主流程
                    pass

                # 保存最终结果
                result = AITaskWorker._json_safe(
                    {
                        "success": True,
                        "stt_text": stt_response.text,
                        "character_response": llm_result["character_response"].content,
                        "audio_url": audio_url,
                        "voice_used": voice_used,
                        "user_message_id": llm_result["user_message"].id,
                        "character_message_id": llm_result["character_message"].id,
                        "usage": llm_result["character_response"].usage,
                    }
                )

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                db.add(task)
                db.commit()

                logger.info(f"语音消息任务处理完成: {task_id}")
                return result

            except Exception as e:
                logger.error(f"语音消息任务处理失败: {task_id}, 错误: {str(e)}")

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                db.add(task)
                db.commit()

                return {"success": False, "error": str(e)}

    def process_text_message_task(self, task_id: str) -> Dict[str, Any]:
        """处理文本消息任务"""
        logger.info(f"开始处理文本消息任务: {task_id}")

        with Session(engine) as db:
            try:
                # 获取任务
                statement = select(AITask).where(AITask.id == task_id)
                task = db.exec(statement).first()

                if not task:
                    logger.error(f"任务不存在: {task_id}")
                    return {"success": False, "error": "任务不存在"}

                # 更新任务状态为处理中
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.utcnow()
                db.add(task)
                db.commit()

                # 解析输入数据
                input_data = TextMessageTaskInput(**task.input_data)

                # 步骤1: LLM - 生成回复
                logger.info(f"开始LLM处理: {task_id}")
                task.progress = 20
                db.add(task)
                db.commit()

                # 调用对话编排服务生成回复
                llm_result = self._run_sync_call(
                    dialogue_orchestration_service.process_user_message,
                    db=db,
                    conversation_id=task.conversation_id,
                    user_message=input_data.message,
                    user_id=task.user_id,
                    settings=None,
                )

                if not llm_result["success"]:
                    raise ValueError(f"LLM处理失败: {llm_result['error']}")

                # 更新LLM步骤完成
                task.progress = 50
                for step in task.steps:
                    if step.get("name") == "llm":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {
                            "content": llm_result["character_response"].content
                        }
                        break
                db.add(task)
                db.commit()

                # 步骤2: TTS - 文本转语音（可选）
                audio_url = None
                voice_used = None

                if input_data.enable_tts and llm_result["character_response"].content:
                    logger.info(f"开始TTS处理: {task_id}")
                    task.progress = 70
                    db.add(task)
                    db.commit()

                    # 使用默认音色
                    voice = "Cherry"

                    tts_request = TTSRequest(
                        text=llm_result["character_response"].content,
                        voice=voice,
                        audio_format="wav",
                        sample_rate=24000,
                    )

                    tts_response = self._run_sync_call(
                        tts_service.synthesize, tts_request
                    )

                    if tts_response.audio_bytes:
                        # 保存音频文件到云存储
                        import os
                        import tempfile

                        from app.services.qiniu_storage_service import (
                            qiniu_storage_service,
                        )

                        with tempfile.NamedTemporaryFile(
                            delete=False, suffix=".wav"
                        ) as temp_file:
                            temp_file.write(tts_response.audio_bytes)
                            temp_file_path = temp_file.name

                        try:
                            upload_result = qiniu_storage_service.upload_audio_file(
                                file_path=temp_file_path,
                                user_id=str(task.user_id),
                                conversation_id=str(task.conversation_id),
                                file_type="tts_audio",
                            )
                            audio_url = upload_result.get("url", "")
                            voice_used = voice
                        finally:
                            if os.path.exists(temp_file_path):
                                os.unlink(temp_file_path)

                # 更新TTS步骤完成
                task.progress = 100
                for step in task.steps:
                    if step.get("name") == "tts":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {"audio_url": audio_url, "voice": voice_used}
                        break
                db.add(task)
                db.commit()

                # 保存最终结果
                result = AITaskWorker._json_safe(
                    {
                        "success": True,
                        "character_response": llm_result["character_response"].content,
                        "audio_url": audio_url,
                        "voice_used": voice_used,
                        "user_message_id": llm_result["user_message"].id,
                        "character_message_id": llm_result["character_message"].id,
                        "usage": llm_result["character_response"].usage,
                    }
                )

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                db.add(task)
                db.commit()

                logger.info(f"文本消息任务处理完成: {task_id}")
                return result

            except Exception as e:
                logger.error(f"文本消息任务处理失败: {task_id}, 错误: {str(e)}")

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                db.add(task)
                db.commit()

                return {"success": False, "error": str(e)}

    def process_tts_generation_task(self, task_id: str) -> Dict[str, Any]:
        """处理TTS生成任务"""
        logger.info(f"开始处理TTS生成任务: {task_id}")

        with Session(engine) as db:
            try:
                # 获取任务
                statement = select(AITask).where(AITask.id == task_id)
                task = db.exec(statement).first()

                if not task:
                    logger.error(f"任务不存在: {task_id}")
                    return {"success": False, "error": "任务不存在"}

                # 更新任务状态为处理中
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.utcnow()
                db.add(task)
                db.commit()

                # 解析输入数据
                input_data = TTSGenerationTaskInput(**task.input_data)

                # TTS处理
                logger.info(f"开始TTS处理: {task_id}")
                task.progress = 50
                db.add(task)
                db.commit()

                tts_request = TTSRequest(
                    text=input_data.text,
                    voice=input_data.voice,
                    audio_format=input_data.audio_format,
                    sample_rate=input_data.sample_rate,
                )

                tts_response = self._run_sync_call(tts_service.synthesize, tts_request)

                # 兼容两种返回：audio_bytes 或 audio_url
                audio_url = None
                audio_bytes = getattr(tts_response, "audio_bytes", None)
                direct_url = getattr(tts_response, "audio_url", None)

                if audio_bytes:
                    # 保存音频文件到云存储
                    import os
                    import tempfile

                    from app.services.qiniu_storage_service import qiniu_storage_service

                    with tempfile.NamedTemporaryFile(
                        delete=False, suffix=".wav"
                    ) as temp_file:
                        temp_file.write(audio_bytes)
                        temp_file_path = temp_file.name

                    try:
                        upload_result = qiniu_storage_service.upload_audio_file(
                            file_path=temp_file_path,
                            user_id=str(task.user_id),
                            file_type="tts_audio",
                        )
                        audio_url = upload_result.get("url", "")
                    finally:
                        if os.path.exists(temp_file_path):
                            os.unlink(temp_file_path)
                elif direct_url:
                    audio_url = direct_url
                else:
                    raise ValueError("TTS生成失败：无音频数据")

                # 更新TTS步骤完成
                task.progress = 100
                for step in task.steps:
                    if step.get("name") == "tts":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {"audio_url": audio_url}
                        break
                db.add(task)
                db.commit()

                # 保存最终结果
                result = {
                    "success": True,
                    "audio_url": audio_url,
                    "voice": input_data.voice,
                    "duration_sec": getattr(tts_response, "duration_sec", None),
                    "model": getattr(tts_response, "model", None),
                }

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                db.add(task)
                db.commit()

                logger.info(f"TTS生成任务处理完成: {task_id}")
                return result

            except Exception as e:
                logger.error(f"TTS生成任务处理失败: {task_id}, 错误: {str(e)}")

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                db.add(task)
                db.commit()

                return {"success": False, "error": str(e)}

    def process_stt_transcription_task(self, task_id: str) -> Dict[str, Any]:
        """处理STT转录任务"""
        logger.info(f"开始处理STT转录任务: {task_id}")

        with Session(engine) as db:
            try:
                # 获取任务
                statement = select(AITask).where(AITask.id == task_id)
                task = db.exec(statement).first()

                if not task:
                    logger.error(f"任务不存在: {task_id}")
                    return {"success": False, "error": "任务不存在"}

                # 更新任务状态为处理中
                task.status = TaskStatus.PROCESSING
                task.started_at = datetime.utcnow()
                db.add(task)
                db.commit()

                # 解析输入数据
                input_data = STTTranscriptionTaskInput(**task.input_data)

                # STT处理
                logger.info(f"开始STT处理: {task_id}")
                task.progress = 50
                db.add(task)
                db.commit()

                stt_request = STTRequest(
                    audio_url=input_data.audio_url,
                    model=input_data.model,
                    prompt=input_data.prompt,
                )

                stt_response = self._run_sync_call(stt_service.transcribe, stt_request)

                if not stt_response.text:
                    raise ValueError("STT转录失败")

                # 更新STT步骤完成
                task.progress = 100
                for step in task.steps:
                    if step.get("name") == "stt":
                        step["status"] = TaskStatus.COMPLETED.value
                        step["completed_at"] = datetime.utcnow().isoformat()
                        step["result"] = {"text": stt_response.text}
                        break
                db.add(task)
                db.commit()

                # 保存最终结果
                result = AITaskWorker._json_safe(
                    {
                        "success": True,
                        "text": stt_response.text,
                        "language": stt_response.language,
                        "duration_sec": stt_response.duration_sec,
                        "model": stt_response.model,
                        "words": stt_response.words,
                    }
                )

                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.result = result
                db.add(task)
                db.commit()

                logger.info(f"STT转录任务处理完成: {task_id}")
                return result

            except Exception as e:
                logger.error(f"STT转录任务处理失败: {task_id}, 错误: {str(e)}")

                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                db.add(task)
                db.commit()

                return {"success": False, "error": str(e)}


# 全局Worker实例
ai_task_worker = AITaskWorker()


# 模块级包装函数，供RQ通过可导入路径调用（避免实例方法无法直接导入）
def process_voice_message_task(task_id: str) -> Dict[str, Any]:
    return ai_task_worker.process_voice_message_task(task_id)


def process_text_message_task(task_id: str) -> Dict[str, Any]:
    return ai_task_worker.process_text_message_task(task_id)


def process_tts_generation_task(task_id: str) -> Dict[str, Any]:
    return ai_task_worker.process_tts_generation_task(task_id)


def process_stt_transcription_task(task_id: str) -> Dict[str, Any]:
    return ai_task_worker.process_stt_transcription_task(task_id)
