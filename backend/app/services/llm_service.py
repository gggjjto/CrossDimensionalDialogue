import logging
from typing import List, Optional, Dict

import dashscope
from dashscope import Generation

from sqlmodel import Session

from app.models.character import Character
from app.models.conversation import Conversation, Message
from app.models.conversation import SenderType
from app.crud.conversation import message as message_crud
from app.core.config import settings
logger = logging.getLogger(__name__)


class LLMRequest:
    """LLM请求模型"""

    def __init__(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        model: Optional[str] = None,
    ):
        self.messages = messages
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.model = model or "qwen-plus"


class LLMResponse:
    """LLM响应模型"""

    def __init__(
        self,
        content: str,
        model: str,
        usage: Optional[Dict[str, int]] = None,
        finish_reason: Optional[str] = None,
    ):
        self.content = content
        self.model = model
        self.usage = usage or {}
        self.finish_reason = finish_reason


class LLMService:
    """LLM服务类 - 使用AI模块"""

    def __init__(self):
        # 初始化 dashscope api_key
        dashscope.api_key = settings.QWEN_API_KEY

    async def generate_character_response(
        self,
        character: Character,
        conversation: Optional[Conversation] = None,
        user_message: str = "",
        session: Optional[Session] = None,
        conversation_history: Optional[List[Message]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        生成角色回复 - 调用 qwen-plus 模型
        """
        try:
            # 构建消息
            if conversation_history:
                messages = conversation_history
            elif conversation and session:
                messages = self._build_messages(character, conversation, user_message, session)
            else:
                # 只用用户消息
                messages = [
                    {"role": "system", "content": self._build_system_prompt(character)},
                    {"role": "user", "content": user_message},
                ]

            # 调用 qwen-plus 模型
            response = Generation.call(
                model="qwen-plus",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            content = response.output.text
            usage = {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

            return LLMResponse(
                content=content,
                model="qwen-plus",
                usage=usage
            )

        except Exception as e:
            logger.error(f"生成角色回复失败: {str(e)}")
            return LLMResponse(
                content="抱歉，我现在无法回复。请稍后再试。",
                model="fallback",
                usage={},
            )

    def _build_messages(
        self,
        character: Character,
        conversation: Conversation,
        user_message: str,
        session: Session,
    ) -> List[Dict[str, str]]:
        messages = []
        system_prompt = self._build_system_prompt(character)
        messages.append({"role": "system", "content": system_prompt})

        recent_messages = message_crud.get_recent_messages(
            session, conversation_id=conversation.id, limit=30
        )

        for msg in recent_messages:
            if msg.sender_type == SenderType.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.sender_type == SenderType.CHARACTER:
                messages.append({"role": "assistant", "content": msg.content})

        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_system_prompt(self, character: Character) -> str:
        prompt_parts = []
        prompt_parts.append(f"你是{character.name}。")
        if character.short_bio:
            prompt_parts.append(f"简介：{character.short_bio}")
        if character.persona_text:
            prompt_parts.append(f"角色设定：{character.persona_text}")
        if character.example_lines:
            prompt_parts.append("示例台词：")
            for line in character.example_lines:
                prompt_parts.append(f"- {line}")
        prompt_parts.extend(
            [
                "",
                "请按照以上设定进行对话，保持角色的一致性。",
                "回复要自然、有趣，符合角色的性格特点。",
                "每次回复控制在200字以内。",
            ]
        )
        return "\n".join(prompt_parts)


# 全局LLM服务实例
llm_service = LLMService()
