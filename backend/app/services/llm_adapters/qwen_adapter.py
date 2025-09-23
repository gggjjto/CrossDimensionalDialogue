"""
阿里千问LLM适配器
"""

import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI

from .base import BaseLLMAdapter

logger = logging.getLogger(__name__)


class QwenLLMAdapter(BaseLLMAdapter):
    """阿里千问LLM适配器"""

    def __init__(
        self,
        api_key: str,
        model_name: str = "qwen-turbo",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ):
        """
        初始化千问适配器

        Args:
            api_key: 千问API密钥
            model_name: 模型名称
            base_url: API基础URL
        """
        super().__init__(api_key, model_name, base_url)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

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
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            choice = response.choices[0]
            content = choice.message.content or ""

            return {
                "content": content,
                "model": self.model_name,
                "usage": (
                    {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens,
                    }
                    if response.usage
                    else {}
                ),
                "finish_reason": choice.finish_reason,
            }

        except Exception as e:
            logger.error(f"千问调用失败: {str(e)}")
            raise Exception(f"千问调用失败: {str(e)}")
