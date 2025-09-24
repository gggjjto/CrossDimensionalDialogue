"""
AI模块配置
定义AI模型与供应商的配置映射
"""

from typing import Dict, Any, Optional
from enum import Enum

from app.core.config import settings


class AIModality(Enum):
    """AI模态类型"""

    TEXT_TO_TEXT = "text_to_text"  # 文生文
    TEXT_TO_IMAGE = "text_to_image"  # 文生图
    IMAGE_TO_TEXT = "image_to_text"  # 图生文
    TEXT_TO_EMBEDDING = "text_to_embedding"  # 文生向量


class AIProvider(Enum):
    """AI提供商类型"""

    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    ALIYUN = "aliyun"


# AI模型配置映射
AI_MODULE_CONFIG: Dict[str, Dict[str, Any]] = {
    # 文生文配置
    "deepseek_chat": {
        "provider": AIProvider.DEEPSEEK.value,
        "modality": AIModality.TEXT_TO_TEXT.value,
        "model": settings.DEEPSEEK_MODEL,
        "api_key": settings.DEEPSEEK_API_KEY,
        "base_url": settings.DEEPSEEK_BASE_URL,
    },
    "qwen_chat": {
        "provider": AIProvider.QWEN.value,
        "modality": AIModality.TEXT_TO_TEXT.value,
        "model": settings.QWEN_CHAT_MODEL,
        "api_key": settings.QWEN_API_KEY,
        "base_url": None,
    },
    # 文生图配置
    "qwen_image": {
        "provider": AIProvider.QWEN.value,
        "modality": AIModality.TEXT_TO_IMAGE.value,
        "model": settings.QWEN_IMAGE_MODEL,
        "api_key": settings.QWEN_API_KEY,
        "base_url": None,
    },
    # 向量嵌入配置
    "qwen_embedding": {
        "provider": AIProvider.QWEN.value,
        "modality": AIModality.TEXT_TO_EMBEDDING.value,
        "model": settings.QWEN_EMBEDDING_MODEL,
        "api_key": settings.QWEN_API_KEY,
        "base_url": None,
    },
}


def get_config_by_provider_and_modality(
    provider: str, modality: str, model: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    根据提供商和模态获取配置

    Args:
        provider: 提供商名称
        modality: 模态类型
        model: 特定模型名称（可选）

    Returns:
        配置字典或None
    """
    for config_key, config in AI_MODULE_CONFIG.items():
        if (
            config["provider"] == provider
            and config["modality"] == modality
            and (model is None or config["model"] == model)
        ):
            return config
    return None


def get_available_configs() -> Dict[str, Dict[str, Any]]:
    """
    获取所有可用的配置

    Returns:
        所有配置的字典
    """
    return AI_MODULE_CONFIG.copy()
