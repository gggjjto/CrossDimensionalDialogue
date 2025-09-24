"""
对话编排服务
负责协调用户消息、角色persona、历史消息，调用LLM生成角色回复
"""

import uuid
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from sqlmodel import Session

from app.models.conversation import (
    Conversation,
    Message,
    MessageCreate,
    SenderType,
    ContentType,
    ConversationSettings,
)
from app.models.character import Character
from app.crud.conversation import conversation, message as message_crud
from app.services.llm_service import llm_service, LLMResponse
from app.services.tts_service import tts_service, TTSRequest, TTSResponse
from app.services.stt_service import stt_service, STTRequest, STTResponse
from app.services.voice_catalog_service import list_voices
from app.services.qiniu_storage_service import QiniuStorageService
import tempfile
import os

logger = logging.getLogger(__name__)


class DialogueOrchestrationService:
    """对话编排服务类"""

    def __init__(self):
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.storage_service = QiniuStorageService()

    async def process_user_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        user_message: str,
        user_id: uuid.UUID,
        settings: Optional[ConversationSettings] = None,
    ) -> Dict[str, Any]:
        """
        处理用户消息并生成角色回复

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            user_message: 用户消息内容
            user_id: 用户ID
            settings: 会话设置

        Returns:
            Dict[str, Any]: 处理结果，包含角色回复和元数据
        """
        try:
            # 获取会话信息
            db_conversation = conversation.get_by_user_and_id(
                db, id=conversation_id, user_id=user_id
            )
            if not db_conversation:
                raise ValueError("会话不存在或无权限访问")

            # 保存用户消息
            user_message_obj = await self._save_user_message(
                db, conversation_id, user_message, user_id
            )

            # 单角色模式 - 获取会话关联的角色
            character = db_conversation.character
            if not character:
                raise ValueError("角色信息不存在")

            # 生成角色回复
            character_response = await self._generate_character_response(
                db, character, db_conversation, user_message, settings
            )

            # 保存角色回复
            character_message_obj = await self._save_character_message(
                db, conversation_id, character_response.content, character.id
            )

            # 更新会话统计
            await self._update_conversation_stats(db, db_conversation)

            # 生成语音回复（如果启用）
            audio_url = None
            if settings and settings.enable_tts and character_response.content:
                audio_url = await self._generate_voice_response(
                    character_response.content,
                    character.name,
                    db,
                    user_id,
                    conversation_id,
                )

            return {
                "success": True,
                "user_message": user_message_obj,
                "character_message": character_message_obj,
                "character_response": character_response,
                "audio_url": audio_url,
                "usage": character_response.usage,
            }

        except Exception as e:
            logger.error(f"处理用户消息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_message": None,
                "character_message": None,
            }

    async def _save_user_message(
        self, db: Session, conversation_id: uuid.UUID, content: str, user_id: uuid.UUID
    ) -> Message:
        """保存用户消息"""
        message_create = MessageCreate(
            content=content,
            content_type=ContentType.TEXT,
            sender_type=SenderType.USER,
            sender_id=user_id,
            status="sent",
        )

        db_message = message_crud.create(
            db, obj_in=message_create, conversation_id=conversation_id
        )

        logger.info(f"用户消息已保存: {db_message.id}")
        return db_message

    async def _generate_character_response(
        self,
        db: Session,
        character: Character,
        conversation: Conversation,
        user_message: str,
        settings: ConversationSettings,
    ) -> LLMResponse:
        """生成角色回复"""
        try:
            # 生成回复
            response = await self.llm_service.generate_character_response(
                character=character,
                conversation=conversation,
                user_message=user_message,
                session=db,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
            )

            logger.info(
                f"角色回复生成成功: {character.name} (使用{settings.llm_provider})"
            )
            return response

        except Exception as e:
            logger.error(f"生成角色回复失败: {str(e)}")
            # 返回默认回复
            return LLMResponse(
                content=f"抱歉，我现在无法回复。请稍后再试。",
                model="fallback",
                usage={},
            )

    async def _save_character_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        content: str,
        character_id: uuid.UUID,
    ) -> Message:
        """保存角色消息"""
        message_create = MessageCreate(
            content=content,
            content_type=ContentType.TEXT,
            sender_type=SenderType.CHARACTER,
            sender_id=character_id,
            status="sent",
        )

        db_message = message_crud.create(
            db, obj_in=message_create, conversation_id=conversation_id
        )

        logger.info(f"角色消息已保存: {db_message.id}")
        return db_message

    async def _update_conversation_stats(self, db: Session, conversation: Conversation):
        """更新会话统计信息"""
        conversation.message_count += 2  # 用户消息 + 角色回复
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        db.add(conversation)
        db.commit()

        logger.info(f"会话统计已更新: {conversation.id}")

    async def _generate_voice_response(
        self,
        text: str,
        character: Character,
        db: Session,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
    ) -> Optional[str]:
        """生成语音回复"""
        try:
            if not text or not text.strip():
                logger.warning("文本为空，跳过语音生成")
                return None

            # 获取可用的音色列表
            available_voices = list_voices(db, provider="qwen3-tts")
            if not available_voices:
                logger.warning("没有可用的音色，使用默认音色")
                voice = "Cherry"  # 默认音色
            else:
                # 使用角色的默认音色
                voice = self._get_character_default_voice(character, available_voices)

            # 创建TTS请求
            tts_request = TTSRequest(
                text=text,
                voice=voice,
                audio_format="wav",
                sample_rate=24000,
            )

            # 调用TTS服务生成语音
            tts_response = await tts_service.synthesize(tts_request)

            if tts_response.audio_bytes:
                # 保存音频文件到云存储
                audio_url = await self._save_audio_to_storage(
                    tts_response.audio_bytes, user_id, conversation_id, character.name
                )
                logger.info(
                    f"为角色 {character.name} 生成语音回复成功，使用音色: {voice}"
                )
                return audio_url
            else:
                logger.error("TTS服务返回空音频数据")
                return None

        except Exception as e:
            logger.error(f"生成语音回复失败: {str(e)}")
            return None

    async def _save_audio_to_storage(
        self,
        audio_bytes: bytes,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        character_name: str,
    ) -> str:
        """保存音频文件到云存储"""
        try:
            # 创建临时文件

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            try:
                # 上传到云存储
                upload_result = self.storage_service.upload_audio_file(
                    file_path=temp_file_path,
                    user_id=str(user_id),
                    conversation_id=str(conversation_id),
                    file_type="tts_audio",
                )

                # 返回云存储URL
                return upload_result.get("url", "")

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"保存音频文件到云存储失败: {str(e)}")
            # 如果云存储失败，返回base64编码的音频数据作为备选
            return f"data:audio/wav;base64,{self._encode_audio_to_base64(audio_bytes)}"

    def _get_default_voice(self, available_voices: List) -> str:
        """获取默认音色"""
        # 优先使用Cherry音色
        for voice_obj in available_voices:
            if voice_obj.voice == "Cherry" and voice_obj.is_active:
                return voice_obj.voice

        # 如果Cherry不可用，使用第一个可用音色
        if available_voices:
            return available_voices[0].voice

        return "Cherry"  # 最终默认音色

    def _get_character_default_voice(
        self, character: Character, available_voices: List
    ) -> str:
        """获取角色的默认音色"""
        # 优先使用角色设置的默认音色
        if character.default_voice:
            for voice_obj in available_voices:
                if voice_obj.voice == character.default_voice and voice_obj.is_active:
                    return voice_obj.voice

        # 如果角色没有设置默认音色或音色不可用，使用全局默认音色
        return self._get_default_voice(available_voices)

    def _encode_audio_to_base64(self, audio_bytes: bytes) -> str:
        """将音频字节编码为base64字符串"""
        import base64

        return base64.b64encode(audio_bytes).decode("utf-8")

    async def process_voice_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        audio_url: str,
        user_id: uuid.UUID,
        settings: Optional[ConversationSettings] = None,
        voice_preference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        处理用户语音消息并生成角色语音回复

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            audio_url: 音频文件的公网URL
            user_id: 用户ID
            settings: 会话设置
            voice_preference: 偏好的音色

        Returns:
            Dict[str, Any]: 处理结果，包含文本回复、语音回复和元数据
        """
        try:
            # 1. 获取会话信息
            db_conversation = conversation.get_by_user_and_id(
                db, id=conversation_id, user_id=user_id
            )
            if not db_conversation:
                raise ValueError("会话不存在或无权限访问")

            # 2. 语音转文本 (STT)
            stt_text = await self._speech_to_text(audio_url)
            if not stt_text:
                raise ValueError("语音识别失败，无法获取文本内容")

            # 3. 保存用户语音消息（以文本形式）
            user_message_obj = await self._save_user_message(
                db, conversation_id, stt_text, user_id
            )

            # 4. 获取角色信息
            character = db_conversation.character
            if not character:
                raise ValueError("角色信息不存在")

            # 5. 生成角色文本回复 (LLM)
            character_response = await self._generate_character_response(
                db, character, db_conversation, stt_text, settings
            )

            # 6. 保存角色文本回复
            character_message_obj = await self._save_character_message(
                db, conversation_id, character_response.content, character.id
            )

            # 7. 更新会话统计
            await self._update_conversation_stats(db, db_conversation)

            # 8. 生成语音回复（如果启用）
            audio_response_url = None
            voice_used = None
            if settings and settings.enable_tts and character_response.content:
                audio_response_url, voice_used = (
                    await self._generate_voice_response_with_preference(
                        character_response.content,
                        character,
                        db,
                        user_id,
                        conversation_id,
                        voice_preference,
                    )
                )

            return {
                "success": True,
                "user_message": user_message_obj,
                "character_message": character_message_obj,
                "character_response": character_response,
                "stt_text": stt_text,
                "text_response": character_response.content,
                "audio_response_url": audio_response_url,
                "voice_used": voice_used,
                "usage": character_response.usage,
            }

        except Exception as e:
            logger.error(f"处理语音消息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "user_message": None,
                "character_message": None,
                "stt_text": None,
                "text_response": None,
                "audio_response_url": None,
                "voice_used": None,
            }

    async def _speech_to_text(self, audio_url: str) -> Optional[str]:
        """语音转文本"""
        try:
            if not audio_url or not audio_url.startswith("http"):
                logger.error("音频URL无效")
                return None

            # 创建STT请求
            stt_request = STTRequest(
                audio_url=audio_url,
                model="qwen3-asr-flash",
                response_format="json",
            )

            # 调用STT服务
            stt_response = await stt_service.transcribe(stt_request)

            if stt_response.text and stt_response.text.strip():
                logger.info(f"语音识别成功: {stt_response.text[:50]}...")
                return stt_response.text.strip()
            else:
                logger.error("STT服务返回空文本")
                return None

        except Exception as e:
            logger.error(f"语音转文本失败: {str(e)}")
            return None

    async def _generate_voice_response_with_preference(
        self,
        text: str,
        character: Character,
        db: Session,
        user_id: uuid.UUID,
        conversation_id: uuid.UUID,
        voice_preference: Optional[str] = None,
    ) -> tuple[Optional[str], Optional[str]]:
        """根据偏好生成语音回复"""
        try:
            if not text or not text.strip():
                logger.warning("文本为空，跳过语音生成")
                return None, None

            # 获取可用的音色列表
            available_voices = list_voices(db, provider="qwen3-tts")
            if not available_voices:
                logger.warning("没有可用的音色，使用默认音色")
                voice = "Cherry"  # 默认音色
            else:
                # 优先使用用户偏好的音色
                if voice_preference:
                    voice = self._select_preferred_voice(
                        voice_preference, available_voices
                    )
                else:
                    # 使用角色的默认音色
                    voice = self._get_character_default_voice(
                        character, available_voices
                    )

            # 创建TTS请求
            tts_request = TTSRequest(
                text=text,
                voice=voice,
                audio_format="wav",
                sample_rate=24000,
            )

            # 调用TTS服务生成语音
            tts_response = await tts_service.synthesize(tts_request)

            if tts_response.audio_bytes:
                # 保存音频文件到云存储
                audio_url = await self._save_audio_to_storage(
                    tts_response.audio_bytes, user_id, conversation_id, character.name
                )
                logger.info(
                    f"为角色 {character.name} 生成语音回复成功，使用音色: {voice}"
                )
                return audio_url, voice
            else:
                logger.error("TTS服务返回空音频数据")
                return None, None

        except Exception as e:
            logger.error(f"生成语音回复失败: {str(e)}")
            return None, None

    def _select_preferred_voice(
        self, voice_preference: str, available_voices: List
    ) -> str:
        """选择用户偏好的音色"""
        for voice_obj in available_voices:
            if voice_obj.voice == voice_preference and voice_obj.is_active:
                return voice_obj.voice

        # 如果偏好音色不可用，使用默认音色Cherry
        return self._get_default_voice(available_voices)

    async def get_conversation_context(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        获取会话上下文

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            user_id: 用户ID
            limit: 消息数量限制

        Returns:
            Dict[str, Any]: 会话上下文信息
        """
        try:
            # 获取会话信息
            db_conversation = conversation.get_by_user_and_id(
                db, id=conversation_id, user_id=user_id
            )
            if not db_conversation:
                raise ValueError("会话不存在或无权限访问")

            # 获取最近消息
            recent_messages = message_crud.get_recent_messages(
                db, conversation_id=conversation_id, limit=limit
            )

            # 获取角色信息
            character = db_conversation.character

            return {
                "conversation": db_conversation,
                "character": character,
                "recent_messages": recent_messages,
                "message_count": len(recent_messages),
                "context_window_size": limit,
            }

        except Exception as e:
            logger.error(f"获取会话上下文失败: {str(e)}")
            raise


# 全局对话编排服务实例
dialogue_orchestration_service = DialogueOrchestrationService()
