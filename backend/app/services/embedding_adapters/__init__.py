"""
嵌入模型适配器模块
"""

from .base import BaseEmbeddingAdapter
from .openai_adapter import OpenAIEmbeddingAdapter
from .aliyun_adapter import AliyunEmbeddingAdapter

__all__ = [
    "BaseEmbeddingAdapter",
    "OpenAIEmbeddingAdapter", 
    "AliyunEmbeddingAdapter",
]
