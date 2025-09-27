"""
对话编排服务
负责协调用户消息、角色persona、历史消息，调用LLM生成角色回复
"""

import os
import tempfile
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.logger import get_logger
from app.crud.conversation import conversation
from app.crud.conversation import message as message_crud
from app.models.character import Character
from app.models.conversation import (
    ContentType,
    Conversation,
    ConversationSettings,
    Message,
    MessageCreate,
    SenderType,
)
from app.services.llm_service import LLMResponse, llm_service
from app.services.qiniu_storage_service import QiniuStorageService
from app.services.stt_service import STTRequest, STTResponse, stt_service
from app.services.tts_service import TTSRequest, TTSResponse, tts_service
from app.services.voice_catalog_service import list_voices
from sqlmodel import Session

logger = get_logger("dialogue_orchestration_service")


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
                logger.error("%s,会话不存在或无权限访问", conversation_id)
                raise ValueError("会话不存在或无权限访问")

            # 保存用户消息
            user_message_obj = await self._save_user_message(
                db, conversation_id, user_message, user_id
            )

            # 单角色模式 - 获取会话关联的角色
            character = db_conversation.character
            if not character:
                logger.error("%s,角色信息不存在", character.id)
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
                    character,
                    db,
                    user_id,
                    conversation_id,
                )

                # 持久化到角色消息记录
                try:
                    if audio_url and character_message_obj:
                        character_message_obj.audio_url = audio_url
                        character_message_obj.updated_at = datetime.utcnow()
                        db.add(character_message_obj)
                        db.commit()
                except Exception:
                    # 不因持久化失败而中断
                    pass

            return {
                "success": True,
                "user_message": user_message_obj,
                "character_message": character_message_obj,
                "character_response": character_response,
                "audio_url": audio_url,
                "usage": character_response.usage,
            }

        except Exception as e:
            logger.error("处理用户消息失败: %s", str(e))
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

        logger.info("用户消息已保存: %s", db_message.id)
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
                temperature=settings.temperature if settings else 0.7,
                max_tokens=settings.max_tokens if settings else 1000,
            )

            logger.info(
                "角色回复生成成功: %s, 回复内容: %s", character.name, response.content
            )
            return response

        except Exception as e:
            logger.error("生成角色回复失败: %s", str(e))
            # 返回默认回复
            return LLMResponse(
                content="抱歉，我现在无法回复。请稍后再试。",
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

        logger.info("角色消息已保存: %s, 消息内容: %s", db_message.id, content)
        return db_message

    async def _update_conversation_stats(self, db: Session, conversation: Conversation):
        """更新会话统计信息"""
        conversation.message_count += 2  # 用户消息 + 角色回复
        conversation.last_message_at = datetime.utcnow()
        conversation.updated_at = datetime.utcnow()

        db.add(conversation)
        db.commit()

        logger.info("会话统计已更新: %s", conversation.id)

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

            # 使用角色的默认音色
            voice = character.default_voice
            if not voice:
                logger.warning("角色没有设置默认音色，使用默认音色")
                voice = "Cherry"  # 默认音色

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
                    "为角色 %s 生成语音回复成功，使用音色: %s", character.name, voice
                )
                return audio_url
            else:
                logger.error("TTS服务返回空音频数据")
                return None

        except Exception as e:
            logger.error("生成语音回复失败: %s", str(e))
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
                logger.info("音频文件已保存到云存储: %s", upload_result.get("url", ""))
                return upload_result.get("url", "")

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error("保存音频文件到云存储失败: %s", str(e))
            # 如果云存储失败，返回base64编码的音频数据作为备选
            return f"data:audio/wav;base64,{self._encode_audio_to_base64(audio_bytes)}"

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
            # 0. 为 settings 设置默认值
            if settings == None:
                settings = ConversationSettings()
                settings.enable_tts = True
            # 1. 获取会话信息
            db_conversation = conversation.get_by_user_and_id(
                db, id=conversation_id, user_id=user_id
            )
            if not db_conversation:
                logger.error("会话不存在或无权限访问")
                raise ValueError("会话不存在或无权限访问")

            # 2. 语音转文本 (STT)
            stt_text = await self._speech_to_text(audio_url)
            if not stt_text:
                logger.error("语音识别失败，无法获取文本内容")
                raise ValueError("语音识别失败，无法获取文本内容")

            # 3. 保存用户语音消息（以文本形式），并记录原始音频URL
            user_message_obj = await self._save_user_message(
                db, conversation_id, stt_text, user_id
            )
            try:
                if user_message_obj and audio_url:
                    user_message_obj.audio_url = audio_url
                    user_message_obj.updated_at = datetime.utcnow()
                    db.add(user_message_obj)
                    db.commit()
            except Exception:
                pass

            # 4. 获取角色信息
            character = db_conversation.character
            if not character:
                logger.error("角色信息不存在")
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

            # 8. 生成语音回复（如果启用），并将生成的音频URL写入角色消息
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

                try:
                    if audio_response_url and character_message_obj:
                        character_message_obj.audio_url = audio_response_url
                        character_message_obj.updated_at = datetime.utcnow()
                        db.add(character_message_obj)
                        db.commit()
                except Exception:
                    pass

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
            logger.error("处理语音消息失败: %s", str(e))
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
            stt_request = STTRequest(audio_url=audio_url)

            # 调用STT服务
            stt_response = await stt_service.transcribe(stt_request)

            if stt_response.text and stt_response.text.strip():
                logger.info("语音识别成功: %s...", stt_response.text[:50])
                return stt_response.text.strip()
            else:
                logger.error("STT服务返回空文本")
                raise ValueError("STT服务返回空文本")

        except Exception as e:
            logger.error("语音转文本失败: %s", str(e))
            raise ValueError("语音转文本失败")

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

            # 使用角色的默认音色
            voice = character.default_voice
            if not voice:
                logger.warning("角色没有设置默认音色，使用默认音色")
                voice = "Cherry"  # 默认音色

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
                    "为角色 %s 生成语音回复成功，使用音色: %s", character.name, voice
                )
                return audio_url, voice
            else:
                logger.error("TTS服务返回空音频数据")
                return None, None

        except Exception as e:
            logger.error("生成语音回复失败: %s", str(e))
            return None, None

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
                logger.error("会话不存在或无权限访问")
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
            logger.error("获取会话上下文失败: %s", str(e))
            raise ValueError("获取会话上下文失败")


# 全局对话编排服务实例
dialogue_orchestration_service = DialogueOrchestrationService()
