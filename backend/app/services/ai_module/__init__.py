"""
AI模块 - 统一的AI模型调用接口
解耦提示词和API调用，支持多模态和多供应商
"""

from .service import AIService, ai_service_manager
from .factory import AIProviderFactory
from .config import AI_MODULE_CONFIG
from .adapters import (
    BaseLLMAdapter,
    BaseEmbeddingAdapter,
    DeepSeekLLMAdapter,
    QwenLLMAdapter,
    QwenEmbeddingAdapter,
)

__all__ = [
    "AIService",
    "ai_service_manager",
    "AIProviderFactory",
    "AI_MODULE_CONFIG",
    "BaseLLMAdapter",
    "BaseEmbeddingAdapter",
    "DeepSeekLLMAdapter",
    "QwenLLMAdapter",
    "QwenEmbeddingAdapter",
]
