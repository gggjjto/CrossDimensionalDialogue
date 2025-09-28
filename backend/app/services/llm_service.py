import json
import re
from typing import Dict, List, Optional

import dashscope
from app.core.config import settings
from app.core.logger import get_logger
from app.crud.conversation import message as message_crud
from app.models.character import Character
from app.models.conversation import Conversation, Message, SenderType
from app.schemas.character import CharacterGenerateRequest, CharacterGenerateResponse
from dashscope import Generation
from sqlmodel import Session

logger = get_logger("llm_service")


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
        生成角色回复
        """
        try:
            # 构建消息
            if conversation_history:
                messages = conversation_history
            elif conversation and session:
                messages = self._build_messages(
                    character, conversation, user_message, session
                )
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
                "total_tokens": response.usage.input_tokens
                + response.usage.output_tokens,
            }

            return LLMResponse(content=content, model="qwen-plus", usage=usage)

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
        """构建消息"""
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
                "每次回复控制在100字以内。简短为主,符合聊天的氛围。",
                "可以用表情符号来增加趣味性和表达情感。",
            ]
        )
        return "\n".join(prompt_parts)

    def generate_character_profile(
        self,
        request: CharacterGenerateRequest,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> CharacterGenerateResponse:
        """
        生成角色简介
        """
        try:
            system_prompt = self._build_character_generation_system_prompt()
            user_prompt = self._build_character_generation_user_prompt(request)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            response = Generation.call(
                model="qwen-plus",
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            content = response.output.text
            parsed_result = self._parse_character_generation_response(content, request)

            return parsed_result

        except Exception as e:
            logger.error(f"生成角色简介失败: {str(e)}")
            return None

    def _build_character_generation_system_prompt(self) -> str:
        """构建角色生成系统提示词"""
        return """你是一个专业的角色设定生成器。请根据用户提供的信息，生成一个完整、详细、有趣的角色设定。
请严格按照以下 JSON 格式输出结果（不要包含多余文本或注释）：
{
"name": "角色名称",
"short_bio": "50-100字的角色简介",
"persona_text": "200-300字的详细人格设定",
"example_lines": ["示例对话1", "示例对话2", "示例对话3"],
"suggested_voice": "推荐音色（必须从给定列表中选择）",
"character_analysis": "100-150字的角色分析"
}
要求：
1. 所有文本必须使用中文。
2. 角色设定要生动有趣，有独特的个性。
3. 示例对话要能体现角色的性格特点。
4. 推荐音色必须从以下 17 个选项中选择：
["li", "Sunny", "Dylan", "Jada", "Elias", "Katerina", "Ryan", "Jennifer",
    "Nofish", "Ethan", "Cherry", "Eric", "Kiki", "Rocky", "Peter", "Roy", "Marcus"]
5. 只输出符合上述 JSON 格式的内容，不要额外说明。
"""

    def _build_character_generation_user_prompt(
        self, request: CharacterGenerateRequest
    ) -> str:
        """构建角色生成用户提示词"""
        prompt_parts = []
        prompt_parts.append(f"请为以下角色生成详细设定：")
        prompt_parts.append(f"角色名称：{request.name}")
        prompt_parts.append(f"角色类型：{request.character_type}")

        if request.background:
            prompt_parts.append(f"背景描述：{request.background}")
        prompt_parts.append("\n请生成一个完整、有趣的角色设定。")

        return "\n".join(prompt_parts)

    def _parse_character_generation_response(
        self, content: str, request: CharacterGenerateRequest
    ) -> CharacterGenerateResponse:
        """解析LLM响应为结构化数据"""
        # 尝试提取JSON部分
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            data = json.loads(json_str)
        else:
            logger.error(f"无法解析角色生成响应: {content}")
            raise ValueError("无法解析，请联系管理员")

        return CharacterGenerateResponse(**data)


# 全局LLM服务实例
llm_service = LLMService()
