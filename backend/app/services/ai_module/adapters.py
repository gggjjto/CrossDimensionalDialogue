"""
AI模块适配器包装器
提供与现有适配器接口的兼容性
"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

from .providers import (
    DeepSeekLLMProvider,
    QwenLLMProvider,
    QwenImageProvider,
    QwenEmbeddingProvider,
)
from .factory import AIProviderFactory

logger = logging.getLogger(__name__)


class BaseLLMAdapter(ABC):
    """LLM适配器基类（兼容现有接口）"""

    def __init__(self, api_key: str, model_name: str, base_url: Optional[str] = None):
        """
        初始化适配器

        Args:
            api_key: API密钥
            model_name: 模型名称
            base_url: API基础URL（可选）
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url

    @abstractmethod
    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        生成LLM回复

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数

        Returns:
            Dict[str, Any]: 包含content、usage等信息的响应
        """
        pass

    def get_model_info(self) -> Dict[str, str]:
        """
        获取模型信息

        Returns:
            Dict[str, str]: 模型信息字典
        """
        return {
            "provider": self.__class__.__name__.replace("LLMAdapter", "").lower(),
            "model_name": self.model_name,
            "base_url": self.base_url or "default",
        }


class BaseEmbeddingAdapter(ABC):
    """嵌入适配器基类（兼容现有接口）"""

    def __init__(self, api_key: str, model_name: str, dimension: int):
        """
        初始化适配器

        Args:
            api_key: API 密钥
            model_name: 模型名称
            dimension: 向量维度
        """
        self.api_key = api_key
        self.model_name = model_name
        self.dimension = dimension

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量嵌入列表
        """
        pass

    @abstractmethod
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的向量嵌入

        Args:
            texts: 输入文本列表

        Returns:
            向量嵌入列表的列表
        """
        pass

    def get_model_info(self) -> dict:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        return {
            "provider": self.__class__.__name__.replace("EmbeddingAdapter", "").lower(),
            "model_name": self.model_name,
            "dimension": self.dimension,
        }


class DeepSeekLLMAdapter(BaseLLMAdapter):
    """DeepSeek LLM适配器（使用ai_module）"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "deepseek-chat",
        base_url: str = "https://api.deepseek.com",
    ):
        """
        初始化DeepSeek适配器

        Args:
            api_key: DeepSeek API密钥
            model_name: 模型名称
            base_url: API基础URL
        """
        super().__init__(api_key, model_name, base_url)
        # 使用ai_module的提供商
        self.provider = DeepSeekLLMProvider(api_key, model_name, base_url)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        生成DeepSeek回复

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数

        Returns:
            Dict[str, Any]: 包含content、usage等信息的响应
        """
        return await self.provider.generate_response(
            messages, temperature, max_tokens, top_p
        )


class QwenLLMAdapter(BaseLLMAdapter):
    """阿里千问LLM适配器（使用ai_module）"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-turbo",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ):
        """
        初始化千问适配器

        Args:
            api_key: 千问 API密钥
            model_name: 模型名称
            base_url: API基础URL
        """
        super().__init__(api_key, model_name, base_url)
        # 使用ai_module的提供商
        self.provider = QwenLLMProvider(api_key, model_name, base_url)

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        生成千问回复

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数

        Returns:
            Dict[str, Any]: 包含content、usage等信息的响应
        """
        return await self.provider.generate_response(
            messages, temperature, max_tokens, top_p
        )


class QwenEmbeddingAdapter(BaseEmbeddingAdapter):
    """通义千问嵌入模型适配器（使用ai_module）"""

    def __init__(self, api_key: str, model_name: str = "text-embedding-v4"):
        """
        初始化通义千问适配器

        Args:
            api_key: 通义千问 API 密钥
            model_name: 模型名称
        """
        # 根据模型名称确定维度
        dimension_map = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
            "text-embedding-v4": 1024,  # 通义千问 v4 实际是 1024 维
        }
        dimension = dimension_map.get(model_name, 1024)

        super().__init__(api_key, model_name, dimension)
        # 使用ai_module的提供商
        self.provider = QwenEmbeddingProvider(api_key, model_name)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量嵌入列表
        """
        return await self.provider.generate_embedding(text)

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的向量嵌入

        Args:
            texts: 输入文本列表

        Returns:
            向量嵌入列表的列表
        """
        return await self.provider.generate_embeddings_batch(texts)
