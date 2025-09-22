"""
嵌入模型适配器基类
"""

from abc import ABC, abstractmethod
from typing import List


class BaseEmbeddingAdapter(ABC):
    """嵌入模型适配器基类"""
    
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
            "dimension": self.dimension
        }
