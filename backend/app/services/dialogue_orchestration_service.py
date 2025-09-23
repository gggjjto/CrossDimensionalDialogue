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
    MultiCharacterMode,
)
from app.models.character import Character
from app.crud.conversation import conversation, message as message_crud
from app.services.llm_service import llm_service, LLMResponse, LLMRequest
from app.services.tts_service import tts_service
from app.services.multi_character_service import multi_character_service
from app.services.context_management_service import context_management_service

logger = logging.getLogger(__name__)


class DialogueOrchestrationService:
    """对话编排服务类"""

    def __init__(self):
        self.llm_service = llm_service
        self.tts_service = tts_service
        self.multi_character_service = multi_character_service
        self.context_management_service = context_management_service

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

            # 使用默认设置
            if not settings:
                settings = ConversationSettings()

            # 保存用户消息
            user_message_obj = await self._save_user_message(
                db, conversation_id, user_message, user_id
            )

            # 根据多角色模式选择角色
            if settings.multi_character_mode == MultiCharacterMode.SINGLE:
                # 单角色模式
                character = db_conversation.character
                if not character:
                    raise ValueError("角色信息不存在")

                character_response = await self._generate_character_response(
                    db, character, db_conversation, user_message, settings
                )

                # 保存角色回复
                character_message_obj = await self._save_character_message(
                    db, conversation_id, character_response.content, character.id
                )

            elif settings.multi_character_mode == MultiCharacterMode.MULTIPLE:
                # 多角色模式
                character_responses = await self._generate_multi_character_responses(
                    db, conversation_id, user_message, settings
                )

                # 保存多个角色回复
                character_message_objs = []
                for char_response in character_responses:
                    char_msg_obj = await self._save_character_message(
                        db,
                        conversation_id,
                        char_response["content"],
                        char_response["character_id"],
                    )
                    character_message_objs.append(char_msg_obj)

                # 为了兼容性，使用第一个回复作为主要回复
                character_response = LLMResponse(
                    content=character_responses[0]["content"],
                    model=character_responses[0]["model"],
                    usage=character_responses[0]["usage"],
                )
                character_message_obj = character_message_objs[0]

            else:  # SWITCHING mode
                # 角色切换模式
                selected_character = (
                    self.multi_character_service.select_responding_character(
                        db, conversation_id, user_message, settings
                    )
                )

                if not selected_character:
                    # 如果没有选中角色，使用默认角色
                    character = db_conversation.character
                else:
                    character = selected_character

                character_response = await self._generate_character_response(
                    db, character, db_conversation, user_message, settings
                )

                # 保存角色回复
                character_message_obj = await self._save_character_message(
                    db, conversation_id, character_response.content, character.id
                )

                # 更新角色回复统计
                self.multi_character_service.update_character_response_stats(
                    db, conversation_id, character.id
                )

            # 更新会话统计
            await self._update_conversation_stats(db, db_conversation)

            # 生成语音回复（如果启用）
            audio_url = None
            if settings.enable_tts and character_response.content:
                audio_url = await self._generate_voice_response(
                    character_response.content, character.name
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
            # 构建消息列表
            messages = self.llm_service._build_messages(
                character, conversation, user_message, db
            )

            # 使用指定的提供商生成回复
            if settings.llm_provider and settings.llm_provider != "openai":
                response = await self.llm_service.generate_response_with_provider(
                    messages=messages,
                    provider=settings.llm_provider.value,
                    model=settings.llm_model,
                    temperature=settings.temperature,
                    max_tokens=settings.max_tokens,
                    top_p=settings.top_p,
                )
            else:
                # 使用默认方法
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
        self, text: str, character_name: str
    ) -> Optional[str]:
        """生成语音回复"""
        try:
            # 这里可以调用TTS服务
            # 暂时返回None，后续可以集成TTS服务
            logger.info(f"为角色 {character_name} 生成语音回复")
            return None

        except Exception as e:
            logger.error(f"生成语音回复失败: {str(e)}")
            return None

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

    async def _generate_multi_character_responses(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        user_message: str,
        settings: ConversationSettings,
    ) -> List[Dict[str, Any]]:
        """
        生成多角色回复

        Args:
            db: 数据库会话
            conversation_id: 会话ID
            user_message: 用户消息
            settings: 会话设置

        Returns:
            List[Dict[str, Any]]: 角色回复列表
        """
        # 获取会话中的所有角色
        characters = self.multi_character_service.get_conversation_characters(
            db, conversation_id, active_only=True
        )

        if not characters:
            raise ValueError("没有找到活跃的角色")

        responses = []

        # 为每个角色生成回复
        for char_conv in characters[: settings.max_characters]:
            try:
                character = db.get(Character, char_conv.character_id)
                if not character:
                    continue

                # 构建上下文
                context = (
                    await self.context_management_service.build_conversation_context(
                        db, conversation_id, character.id, user_message, settings
                    )
                )

                # 构建增强的提示词
                enhanced_prompt = self.context_management_service.build_enhanced_prompt(
                    character, context
                )

                # 构建消息列表
                messages = [{"role": "system", "content": enhanced_prompt}]

                # 添加历史消息
                for msg in context["messages"]:
                    role = "user" if msg.sender_type == SenderType.USER else "assistant"
                    messages.append({"role": role, "content": msg.content})

                # 添加当前用户消息
                messages.append({"role": "user", "content": user_message})

                # 调用LLM生成回复
                if settings.llm_provider and settings.llm_provider != "openai":
                    response = await self.llm_service.generate_response_with_provider(
                        messages=messages,
                        provider=settings.llm_provider.value,
                        model=settings.llm_model,
                        temperature=settings.temperature,
                        max_tokens=settings.max_tokens,
                        top_p=settings.top_p,
                    )
                else:
                    response = await self.llm_service.generate_response(
                        LLMRequest(messages=messages)
                    )

                responses.append(
                    {
                        "character_id": character.id,
                        "character_name": character.name,
                        "content": response.content,
                        "model": response.model,
                        "usage": response.usage,
                    }
                )

            except Exception as e:
                logger.error(f"为角色 {char_conv.character_id} 生成回复失败: {str(e)}")
                continue

        return responses


# 全局对话编排服务实例
dialogue_orchestration_service = DialogueOrchestrationService()
