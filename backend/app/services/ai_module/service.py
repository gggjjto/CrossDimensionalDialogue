"""
AI服务核心类
统一管理AI模型调用，解耦提示词和API调用
"""

import logging
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import UUID

from .config import AI_MODULE_CONFIG, AIModality
from .factory import AIProviderFactory
from .prompts import (
    CharacterSystemPrompt,
    CharacterDialoguePrompt,
    GeneralTextPrompt,
    CharacterImagePrompt,
    GeneralImagePrompt,
    ImageAnalysisPrompt,
    ImageDescriptionPrompt,
)

logger = logging.getLogger(__name__)


class AIService:
    """AI服务核心类"""

    def __init__(self, config_key: str):
        """
        初始化AI服务

        Args:
            config_key: 配置键名

        Raises:
            ValueError: 当配置不存在时
        """
        if config_key not in AI_MODULE_CONFIG:
            raise ValueError(f"不支持的配置键: {config_key}")

        self.config_key = config_key
        self.config = AI_MODULE_CONFIG[config_key]
        self.provider = AIProviderFactory.create_provider(config_key)
        self.modality = self.config["modality"]

        logger.info(
            f"AI服务初始化成功: {config_key} - {self.config['provider']}/{self.modality}"
        )

    async def generate_text(self, prompt: Union[str, Dict[str, Any]], **kwargs) -> str:
        """
        生成文本内容

        Args:
            prompt: 提示词字符串或提示词构建参数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        if self.modality != AIModality.TEXT_TO_TEXT.value:
            raise ValueError(f"配置 {self.config_key} 不支持文本生成")

        # 处理提示词
        if isinstance(prompt, str):
            final_prompt = prompt
        else:
            # 使用通用文本提示词构建器
            text_prompt = GeneralTextPrompt()
            final_prompt = text_prompt.build(**prompt)

        return await self.provider.generate(final_prompt, **kwargs)

    async def generate_character_response(
        self,
        character_data: Dict[str, Any],
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        生成角色回复

        Args:
            character_data: 角色数据
            user_message: 用户消息
            conversation_history: 对话历史
            context: 上下文信息
            **kwargs: 其他参数

        Returns:
            角色回复
        """
        if self.modality != AIModality.TEXT_TO_TEXT.value:
            raise ValueError(f"配置 {self.config_key} 不支持文本生成")

        # 构建系统提示词
        system_prompt = CharacterSystemPrompt()
        system_message = system_prompt.build_message(**character_data)

        # 构建对话提示词
        dialogue_prompt = CharacterDialoguePrompt()
        dialogue_content = dialogue_prompt.build(
            user_message=user_message,
            conversation_history=conversation_history,
            context=context,
        )

        # 构建消息列表
        messages = [system_message, {"role": "user", "content": dialogue_content}]

        return await self.provider.generate(messages, **kwargs)

    async def generate_image(
        self, prompt: Union[str, Dict[str, Any]], **kwargs
    ) -> bytes:
        """
        生成图像

        Args:
            prompt: 图像描述字符串或构建参数
            **kwargs: 其他参数

        Returns:
            图像字节数据
        """
        if self.modality != AIModality.TEXT_TO_IMAGE.value:
            raise ValueError(f"配置 {self.config_key} 不支持图像生成")

        # 处理提示词
        if isinstance(prompt, str):
            final_prompt = prompt
        else:
            # 使用通用图像提示词构建器
            image_prompt = GeneralImagePrompt()
            final_prompt = image_prompt.build(**prompt)

        return await self.provider.generate(final_prompt, **kwargs)

    async def generate_character_image(
        self, character_data: Dict[str, Any], **kwargs
    ) -> bytes:
        """
        生成角色图像

        Args:
            character_data: 角色数据
            **kwargs: 其他参数

        Returns:
            角色图像字节数据
        """
        if self.modality != AIModality.TEXT_TO_IMAGE.value:
            raise ValueError(f"配置 {self.config_key} 不支持图像生成")

        # 构建角色图像提示词
        image_prompt = CharacterImagePrompt()

        final_prompt = image_prompt.build(**character_data)

        return await self.provider.generate(final_prompt, **kwargs)

    async def analyze_image(
        self, image_data: bytes, prompt: Union[str, Dict[str, Any]], **kwargs
    ) -> str:
        """
        分析图像

        Args:
            image_data: 图像字节数据
            prompt: 分析提示词或构建参数
            **kwargs: 其他参数

        Returns:
            分析结果文本
        """
        if self.modality != AIModality.IMAGE_TO_TEXT.value:
            raise ValueError(f"配置 {self.config_key} 不支持图像分析")

        # 处理提示词
        if isinstance(prompt, str):
            final_prompt = prompt
        else:
            # 使用图像分析提示词构建器
            analysis_prompt = ImageAnalysisPrompt()
            final_prompt = analysis_prompt.build(**prompt)

        return await self.provider.generate(
            final_prompt, image_data=image_data, **kwargs
        )

    async def generate_embedding(
        self, text: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        生成向量嵌入

        Args:
            text: 输入文本或文本列表
            **kwargs: 其他参数

        Returns:
            向量嵌入
        """
        if self.modality != AIModality.TEXT_TO_EMBEDDING.value:
            raise ValueError(f"配置 {self.config_key} 不支持向量嵌入")

        return await self.provider.generate(text, **kwargs)

    def get_provider_info(self) -> Dict[str, Any]:
        """
        获取提供商信息

        Returns:
            提供商信息字典
        """
        return {
            "config_key": self.config_key,
            "provider": self.config["provider"],
            "modality": self.modality,
            "model": self.config["model"],
            "provider_info": self.provider.get_model_info(),
        }

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息（兼容性方法）

        Returns:
            模型信息字典
        """
        return self.get_provider_info()

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            是否健康
        """
        try:
            return await self.provider.health_check()
        except Exception as e:
            logger.error(f"AI服务健康检查失败 {self.config_key}: {str(e)}")
            return False


class AIServiceManager:
    """AI服务管理器"""

    def __init__(self):
        self._services: Dict[str, AIService] = {}

    def get_service(self, config_key: str) -> AIService:
        """
        获取AI服务实例

        Args:
            config_key: 配置键名

        Returns:
            AI服务实例
        """
        if config_key not in self._services:
            self._services[config_key] = AIService(config_key)

        return self._services[config_key]

    def get_available_services(self) -> List[str]:
        """
        获取所有可用的服务配置键

        Returns:
            配置键列表
        """
        return list(AI_MODULE_CONFIG.keys())

    def get_services_by_modality(self, modality: str) -> List[str]:
        """
        根据模态获取服务配置键

        Args:
            modality: 模态类型

        Returns:
            配置键列表
        """
        return [
            key
            for key, config in AI_MODULE_CONFIG.items()
            if config["modality"] == modality
        ]

    def get_services_by_provider(self, provider: str) -> List[str]:
        """
        根据提供商获取服务配置键

        Args:
            provider: 提供商名称

        Returns:
            配置键列表
        """
        return [
            key
            for key, config in AI_MODULE_CONFIG.items()
            if config["provider"] == provider
        ]


# 全局AI服务管理器实例
ai_service_manager = AIServiceManager()
