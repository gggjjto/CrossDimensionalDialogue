"""
AI提供商工厂
"""

import logging
from typing import Dict, Any, Optional

from .config import AI_MODULE_CONFIG, AIProvider, AIModality
from .providers import (
    DeepSeekLLMProvider,
    QwenLLMProvider,
    QwenImageProvider,
    QwenEmbeddingProvider,
)

logger = logging.getLogger(__name__)


class AIProviderFactory:
    """AI提供商工厂类"""

    @staticmethod
    def create_provider(config_key: str) -> Any:
        """
        根据配置键创建提供商实例

        Args:
            config_key: 配置键名

        Returns:
            提供商实例

        Raises:
            ValueError: 当配置不存在或不支持时
        """
        if config_key not in AI_MODULE_CONFIG:
            raise ValueError(f"不支持的配置键: {config_key}")

        config = AI_MODULE_CONFIG[config_key]
        provider = config["provider"]
        modality = config["modality"]
        model = config["model"]
        api_key = config["api_key"]
        base_url = config.get("base_url")

        if not api_key:
            raise ValueError(f"配置 {config_key} 缺少API密钥")

        try:
            # 根据提供商和模态创建相应的实例
            if provider == AIProvider.DEEPSEEK.value:
                if modality == AIModality.TEXT_TO_TEXT.value:
                    return DeepSeekLLMProvider(api_key, model, base_url)
                else:
                    raise ValueError(f"DeepSeek不支持模态: {modality}")

            elif provider == AIProvider.QWEN.value:
                if modality == AIModality.TEXT_TO_TEXT.value:
                    return QwenLLMProvider(api_key, model, base_url)
                elif modality == AIModality.TEXT_TO_IMAGE.value:
                    return QwenImageProvider(api_key, model, base_url)
                elif modality == AIModality.TEXT_TO_EMBEDDING.value:
                    return QwenEmbeddingProvider(api_key, model, base_url)
                else:
                    raise ValueError(f"通义千问不支持模态: {modality}")

            else:
                raise ValueError(f"不支持的提供商: {provider}")

        except Exception as e:
            logger.error(f"创建提供商失败 {config_key}: {str(e)}")
            raise ValueError(f"创建提供商失败: {str(e)}")

    @staticmethod
    def create_provider_by_params(
        provider: str,
        modality: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
    ) -> Any:
        """
        根据参数创建提供商实例

        Args:
            provider: 提供商名称
            modality: 模态类型
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL（可选）

        Returns:
            提供商实例
        """
        try:
            if provider == AIProvider.DEEPSEEK.value:
                if modality == AIModality.TEXT_TO_TEXT.value:
                    return DeepSeekLLMProvider(api_key, model, base_url)
                else:
                    raise ValueError(f"DeepSeek不支持模态: {modality}")

            elif provider == AIProvider.QWEN.value:
                if modality == AIModality.TEXT_TO_TEXT.value:
                    return QwenLLMProvider(api_key, model, base_url)
                elif modality == AIModality.TEXT_TO_IMAGE.value:
                    return QwenImageProvider(api_key, model, base_url)
                elif modality == AIModality.TEXT_TO_EMBEDDING.value:
                    return QwenEmbeddingProvider(api_key, model, base_url)
                else:
                    raise ValueError(f"通义千问不支持模态: {modality}")

            else:
                raise ValueError(f"不支持的提供商: {provider}")

        except Exception as e:
            logger.error(f"创建提供商失败 {provider}/{modality}: {str(e)}")
            raise ValueError(f"创建提供商失败: {str(e)}")

    @staticmethod
    def get_available_configs() -> Dict[str, Dict[str, Any]]:
        """
        获取所有可用的配置

        Returns:
            所有配置的字典
        """
        return AI_MODULE_CONFIG.copy()

    @staticmethod
    def get_configs_by_provider(provider: str) -> Dict[str, Dict[str, Any]]:
        """
        根据提供商获取配置

        Args:
            provider: 提供商名称

        Returns:
            该提供商的配置字典
        """
        return {
            key: config
            for key, config in AI_MODULE_CONFIG.items()
            if config["provider"] == provider
        }

    @staticmethod
    def get_configs_by_modality(modality: str) -> Dict[str, Dict[str, Any]]:
        """
        根据模态获取配置

        Args:
            modality: 模态类型

        Returns:
            该模态的配置字典
        """
        return {
            key: config
            for key, config in AI_MODULE_CONFIG.items()
            if config["modality"] == modality
        }
