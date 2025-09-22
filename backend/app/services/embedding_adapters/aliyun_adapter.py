"""
阿里云嵌入模型适配器
"""

import logging
from typing import List

import dashscope
from dashscope import TextEmbedding

from .base import BaseEmbeddingAdapter

logger = logging.getLogger(__name__)


class AliyunEmbeddingAdapter(BaseEmbeddingAdapter):
    """阿里云嵌入模型适配器"""
    
    def __init__(self, api_key: str, model_name: str = "text-embedding-v4"):
        """
        初始化阿里云适配器
        
        Args:
            api_key: 阿里云 API 密钥
            model_name: 模型名称
        """
        # 根据模型名称确定维度
        dimension_map = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
            "text-embedding-v4": 1536,
        }
        dimension = dimension_map.get(model_name, 1536)
        
        super().__init__(api_key, model_name, dimension)
        
        # 设置 API 密钥
        dashscope.api_key = api_key
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入
        
        Args:
            text: 输入文本
            
        Returns:
            向量嵌入列表
        """
        try:
            response = TextEmbedding.call(
                model=self.model_name,
                input=text
            )
            
            if response.status_code == 200:
                return response.output['embeddings'][0]['embedding']
            else:
                error_msg = f"阿里云 API 错误: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"阿里云生成向量嵌入失败: {str(e)}")
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
            response = TextEmbedding.call(
                model=self.model_name,
                input=texts
            )
            
            if response.status_code == 200:
                return [item['embedding'] for item in response.output['embeddings']]
            else:
                error_msg = f"阿里云 API 错误: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"阿里云批量生成向量嵌入失败: {str(e)}")
            raise
