"""
LLM服务 V2
使用统一的AI模块进行LLM调用
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session

from app.core.config import settings
from app.models.character import Character
from app.models.conversation import Conversation, Message, SenderType, ContentType
from app.services.ai_module import ai_service_manager

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


class LLMServiceV2:
    """LLM服务类 V2 - 使用AI模块"""

    def __init__(self):
        self.default_config_key = self._get_default_config_key()
        self.ai_service = ai_service_manager.get_service(self.default_config_key)

    def _get_default_config_key(self) -> str:
        """根据配置获取默认的配置键"""
        provider = settings.LLM_PROVIDER.lower()

        if provider == "openai":
            return "openai_gpt"
        elif provider == "deepseek":
            return "deepseek_chat"
        elif provider == "qwen":
            return "qwen_chat"
        else:
            logger.warning(f"不支持的LLM提供商: {provider}，使用默认OpenAI")
            return "openai_gpt"

    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        生成LLM回复

        Args:
            request: LLM请求

        Returns:
            LLMResponse: LLM回复

        Raises:
            Exception: 当LLM调用失败时
        """
        try:
            # 使用AI模块生成文本
            content = await self.ai_service.generate_text(
                request.messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                top_p=request.top_p,
            )

            return LLMResponse(
                content=content,
                model=self.ai_service.config["model"],
                usage={},  # AI模块暂不返回usage信息
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"LLM生成回复失败: {str(e)}")
            raise Exception(f"LLM生成回复失败: {str(e)}")

    async def generate_character_response(
        self,
        character: Character,
        user_message: str,
        conversation_history: Optional[List[Message]] = None,
        context: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> str:
        """
        生成角色回复

        Args:
            character: 角色对象
            user_message: 用户消息
            conversation_history: 对话历史
            context: 上下文信息
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: 角色回复内容
        """
        try:
            # 构建角色数据
            character_data = {
                "character_name": character.name,
                "character_description": character.description or "",
                "personality": character.personality or "",
                "background": character.background or "",
                "speaking_style": character.speaking_style or "",
                "knowledge_base": character.knowledge_base or "",
            }

            # 转换对话历史格式
            history_messages = []
            if conversation_history:
                for msg in conversation_history[-10:]:  # 只保留最近10条
                    if msg.sender_type == SenderType.USER:
                        history_messages.append(
                            {"role": "user", "content": msg.content}
                        )
                    elif msg.sender_type == SenderType.CHARACTER:
                        history_messages.append(
                            {"role": "assistant", "content": msg.content}
                        )

            # 使用AI模块生成角色回复
            response = await self.ai_service.generate_character_response(
                character_data=character_data,
                user_message=user_message,
                conversation_history=history_messages,
                context=context,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            return response

        except Exception as e:
            logger.error(f"生成角色回复失败: {str(e)}")
            raise Exception(f"生成角色回复失败: {str(e)}")

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
        try:
            # 根据提供商选择配置键
            config_key = self._get_config_key_by_provider(provider, model)

            # 获取对应的AI服务
            service = ai_service_manager.get_service(config_key)

            # 生成回复
            content = await service.generate_text(
                messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            return LLMResponse(
                content=content,
                model=service.config["model"],
                usage={},
                finish_reason="stop",
            )

        except Exception as e:
            logger.error(f"使用{provider}生成回复失败: {str(e)}")
            raise Exception(f"使用{provider}生成回复失败: {str(e)}")

    def _get_config_key_by_provider(
        self, provider: str, model: Optional[str] = None
    ) -> str:
        """
        根据提供商获取配置键

        Args:
            provider: 提供商名称
            model: 模型名称（可选）

        Returns:
            str: 配置键
        """
        provider = provider.lower()

        if provider == "openai":
            return "openai_gpt"
        elif provider == "deepseek":
            return "deepseek_chat"
        elif provider == "qwen":
            return "qwen_chat"
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}")

    def get_adapter_for_provider(self, provider: str) -> Optional[Any]:
        """
        根据提供商获取适配器（兼容性方法）

        Args:
            provider: LLM提供商

        Returns:
            AI服务实例或None
        """
        try:
            config_key = self._get_config_key_by_provider(provider)
            return ai_service_manager.get_service(config_key)
        except Exception as e:
            logger.error(f"创建{provider}适配器失败: {str(e)}")
            return None

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            bool: 是否健康
        """
        try:
            return await self.ai_service.health_check()
        except Exception as e:
            logger.error(f"LLM服务健康检查失败: {str(e)}")
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            Dict[str, Any]: 模型信息
        """
        return self.ai_service.get_provider_info()


# 全局LLM服务实例 V2
llm_service_v2 = LLMServiceV2()
