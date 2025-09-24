"""
LLM服务
负责调用大语言模型生成角色回复
支持多种LLM提供商：OpenAI、DeepSeek、阿里千问
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session

from app.core.config import settings
from app.models.character import Character
from app.models.conversation import Conversation, Message, SenderType, ContentType
from app.services.ai_module import (
    BaseLLMAdapter,
    DeepSeekLLMAdapter,
    QwenLLMAdapter,
)

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
        self.model = model or settings.OPENAI_MODEL


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
    """LLM服务类"""

    def __init__(self):
        self.adapter: Optional[BaseLLMAdapter] = None
        self._initialize_adapter()

    def _initialize_adapter(self):
        """初始化LLM适配器"""
        try:
            provider = settings.LLM_PROVIDER.lower()

            if provider == "deepseek":
                if not settings.DEEPSEEK_API_KEY:
                    raise ValueError("DeepSeek API密钥未配置")
                self.adapter = DeepSeekLLMAdapter(
                    api_key=settings.DEEPSEEK_API_KEY,
                    model_name=settings.DEEPSEEK_MODEL,
                    base_url=settings.DEEPSEEK_BASE_URL,
                )
                logger.info(
                    f"DeepSeek适配器初始化成功，模型: {settings.DEEPSEEK_MODEL}"
                )

            elif provider == "qwen":
                if not settings.QWEN_API_KEY:
                    raise ValueError("千问API密钥未配置")
                self.adapter = QwenLLMAdapter(
                    api_key=settings.QWEN_API_KEY,
                    model_name=settings.QWEN_MODEL,
                    base_url=settings.QWEN_BASE_URL,
                )
                logger.info(f"千问适配器初始化成功，模型: {settings.QWEN_MODEL}")

            else:
                raise ValueError(f"不支持的LLM提供商: {provider}")

        except Exception as e:
            logger.error(f"LLM适配器初始化失败: {str(e)}")
            self.adapter = None

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        生成LLM回复

        Args:
            request: LLM请求

        Returns:
            LLMResponse: LLM回复

        Raises:
            ValueError: 当LLM服务不可用时
            Exception: 当LLM调用失败时
        """
        if not self.adapter:
            raise ValueError("LLM服务不可用，请检查API密钥配置")

        try:
            logger.info(f"调用LLM模型: {request.model}")

            response_data = await self.adapter.generate_response(
                messages=request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
            )

            logger.info(f"LLM回复生成成功，长度: {len(response_data['content'])}")

            return LLMResponse(
                content=response_data["content"],
                model=response_data["model"],
                usage=response_data.get("usage", {}),
                finish_reason=response_data.get("finish_reason"),
            )

        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise Exception(f"LLM调用失败: {str(e)}")

    async def generate_character_response(
        self,
        character: Character,
        conversation: Conversation,
        user_message: str,
        session: Session,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """
        为角色生成回复

        Args:
            character: 角色对象
            conversation: 会话对象
            user_message: 用户消息
            session: 数据库会话
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            LLMResponse: 角色回复
        """
        # 构建消息列表
        messages = self._build_messages(character, conversation, user_message, session)

        # 创建LLM请求
        request = LLMRequest(
            messages=messages, temperature=temperature, max_tokens=max_tokens
        )

        # 调用LLM生成回复
        return await self.generate_response(request)

    def _build_messages(
        self,
        character: Character,
        conversation: Conversation,
        user_message: str,
        session: Session,
    ) -> List[Dict[str, str]]:
        """
        构建LLM消息列表

        Args:
            character: 角色对象
            conversation: 会话对象
            user_message: 用户消息
            session: 数据库会话

        Returns:
            List[Dict[str, str]]: 消息列表
        """
        messages = []

        # 添加系统提示词
        system_prompt = self._build_system_prompt(character)
        messages.append({"role": "system", "content": system_prompt})

        # 添加历史消息（最近10条）
        from app.crud.conversation import message as message_crud

        recent_messages = message_crud.get_recent_messages(
            session, conversation_id=conversation.id, limit=10
        )

        for msg in recent_messages:
            if msg.sender_type == SenderType.USER:
                messages.append({"role": "user", "content": msg.content})
            elif msg.sender_type == SenderType.CHARACTER:
                messages.append({"role": "assistant", "content": msg.content})

        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})

        return messages

    def _build_system_prompt(self, character: Character) -> str:
        """
        构建系统提示词

        Args:
            character: 角色对象

        Returns:
            str: 系统提示词
        """
        prompt_parts = []

        # 基础角色设定
        prompt_parts.append(f"你是{character.name}。")

        # 角色简介
        if character.short_bio:
            prompt_parts.append(f"简介：{character.short_bio}")

        # 角色persona
        if character.persona_text:
            prompt_parts.append(f"角色设定：{character.persona_text}")

        # 示例台词
        if character.example_lines:
            prompt_parts.append("示例台词：")
            for line in character.example_lines[:3]:  # 只取前3个示例
                prompt_parts.append(f"- {line}")

        # 对话要求
        prompt_parts.extend(
            [
                "",
                "请按照以上设定进行对话，保持角色的一致性。",
                "回复要自然、有趣，符合角色的性格特点。",
                "每次回复控制在200字以内。",
            ]
        )

        return "\n".join(prompt_parts)

    def get_adapter_for_provider(self, provider: str) -> Optional[BaseLLMAdapter]:
        """
        根据提供商获取适配器

        Args:
            provider: LLM提供商

        Returns:
            BaseLLMAdapter: 对应的适配器实例
        """
        try:
            provider = provider.lower()

            if provider == "openai":
                if not settings.OPENAI_API_KEY:
                    return None
                return OpenAILLMAdapter(
                    api_key=settings.OPENAI_API_KEY, model_name=settings.OPENAI_MODEL
                )

            elif provider == "deepseek":
                if not settings.DEEPSEEK_API_KEY:
                    return None
                return DeepSeekLLMAdapter(
                    api_key=settings.DEEPSEEK_API_KEY,
                    model_name=settings.DEEPSEEK_MODEL,
                    base_url=settings.DEEPSEEK_BASE_URL,
                )

            elif provider == "qwen":
                if not settings.QWEN_API_KEY:
                    return None
                return QwenLLMAdapter(
                    api_key=settings.QWEN_API_KEY,
                    model_name=settings.QWEN_MODEL,
                    base_url=settings.QWEN_BASE_URL,
                )

            else:
                logger.warning(f"不支持的LLM提供商: {provider}")
                return None

        except Exception as e:
            logger.error(f"创建{provider}适配器失败: {str(e)}")
            return None

    async def generate_response_with_provider(
        self,
        messages: List[Dict[str, str]],
        provider: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> LLMResponse:
        """
        使用指定提供商生成回复

        Args:
            messages: 消息列表
            provider: LLM提供商
            model: 模型名称（可选）
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数

        Returns:
            LLMResponse: LLM回复
        """
        adapter = self.get_adapter_for_provider(provider)
        if not adapter:
            raise ValueError(f"无法创建{provider}适配器，请检查配置")

        # 如果指定了模型，临时更新适配器的模型
        original_model = adapter.model_name
        if model:
            adapter.model_name = model

        try:
            response_data = await adapter.generate_response(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            return LLMResponse(
                content=response_data["content"],
                model=response_data["model"],
                usage=response_data.get("usage", {}),
                finish_reason=response_data.get("finish_reason"),
            )

        finally:
            # 恢复原始模型
            if model:
                adapter.model_name = original_model


# 全局LLM服务实例
llm_service = LLMService()
