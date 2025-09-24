"""
通义千问向量嵌入提供商实现
"""

import logging
from typing import List, Union
import dashscope
from dashscope import TextEmbedding

from .base import BaseAIProvider, AIProviderType

logger = logging.getLogger(__name__)


class QwenEmbeddingProvider(BaseAIProvider):
    """通义千问向量嵌入提供商"""

    def __init__(
        self, api_key: str, model: str = "text-embedding-v4", base_url: str = None
    ):
        super().__init__(api_key, model, base_url)
        # 设置API密钥
        dashscope.api_key = api_key

    async def generate(
        self, prompt: Union[str, List[str]], **kwargs
    ) -> Union[List[float], List[List[float]]]:
        """
        生成向量嵌入

        Args:
            prompt: 输入文本或文本列表
            **kwargs: 其他参数

        Returns:
            向量嵌入（单个或批量）
        """
        try:
            if isinstance(prompt, str):
                # 单个文本
                response = TextEmbedding.call(model=self.model, input=prompt)

                if response.status_code == 200:
                    return response.output["embeddings"][0]["embedding"]
                else:
                    error_msg = f"通义千问API错误: {response.code} - {response.message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            else:
                # 批量文本
                embeddings = []
                for text in prompt:
                    response = TextEmbedding.call(model=self.model, input=text)

                    if response.status_code == 200:
                        embeddings.append(response.output["embeddings"][0]["embedding"])
                    else:
                        error_msg = (
                            f"通义千问API错误: {response.code} - {response.message}"
                        )
                        logger.error(error_msg)
                        raise Exception(error_msg)

                return embeddings

        except Exception as e:
            logger.error(f"通义千问向量嵌入生成失败: {str(e)}")
            raise Exception(f"通义千问向量嵌入生成失败: {str(e)}")

    def get_provider_type(self) -> AIProviderType:
        return AIProviderType.QWEN

    def get_dimension(self) -> int:
        """获取向量维度"""
        dimension_map = {
            "text-embedding-v1": 1536,
            "text-embedding-v2": 1536,
            "text-embedding-v4": 1024,
        }
        return dimension_map.get(self.model, 1024)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成文本的向量嵌入（兼容现有适配器接口）

        Args:
            text: 输入文本

        Returns:
            向量嵌入列表
        """
        try:
            response = TextEmbedding.call(model=self.model, input=text)

            if response.status_code == 200:
                return response.output["embeddings"][0]["embedding"]
            else:
                error_msg = f"通义千问 API 错误: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"通义千问生成向量嵌入失败: {str(e)}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本的向量嵌入（兼容现有适配器接口）

        Args:
            texts: 输入文本列表

        Returns:
            向量嵌入列表的列表
        """
        try:
            response = TextEmbedding.call(model=self.model, input=texts)

            if response.status_code == 200:
                return [item["embedding"] for item in response.output["embeddings"]]
            else:
                error_msg = f"通义千问 API 错误: {response.code} - {response.message}"
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"通义千问批量生成向量嵌入失败: {str(e)}")
            raise
