"""
OpenAI 嵌入模型适配器
"""

import logging
from typing import List

from openai import AsyncOpenAI

from .base import BaseEmbeddingAdapter

logger = logging.getLogger(__name__)


class OpenAIEmbeddingAdapter(BaseEmbeddingAdapter):
    """OpenAI 嵌入模型适配器"""
    
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small"):
        """
        初始化 OpenAI 适配器
        
        Args:
            api_key: OpenAI API 密钥
            model_name: 模型名称
        """
        # 根据模型名称确定维度
        dimension_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536,
        }
        dimension = dimension_map.get(model_name, 1536)
        
        super().__init__(api_key, model_name, dimension)
        self.client = AsyncOpenAI(api_key=api_key)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            向量嵌入列表
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=text,
                encoding_format="float"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI 生成向量嵌入失败: {str(e)}")
            raise
    
    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的向量嵌入
        
        Args:
            texts: 输入文本列表
            
        Returns:
            向量嵌入列表的列表
        """
        try:
            response = await self.client.embeddings.create(
                model=self.model_name,
                input=texts,
                encoding_format="float"
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"OpenAI 批量生成向量嵌入失败: {str(e)}")
            raise
