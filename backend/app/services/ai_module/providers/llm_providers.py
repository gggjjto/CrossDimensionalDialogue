"""
LLM提供商实现
"""

import logging
from typing import List, Dict, Any, Union
from openai import AsyncOpenAI

from .base import BaseAIProvider, AIProviderType

logger = logging.getLogger(__name__)


class DeepSeekLLMProvider(BaseAIProvider):
    """DeepSeek LLM提供商"""

    def __init__(
        self, api_key: str, model: str, base_url: str = "https://api.deepseek.com"
    ):
        super().__init__(api_key, model, base_url)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        **kwargs,
    ) -> str:
        """
        生成文本回复

        Args:
            prompt: 提示词或消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        try:
            # 处理提示词格式
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"DeepSeek LLM调用失败: {str(e)}")
            raise Exception(f"DeepSeek LLM调用失败: {str(e)}")

    def get_provider_type(self) -> AIProviderType:
        return AIProviderType.DEEPSEEK

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        生成LLM回复（兼容现有适配器接口）

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
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            choice = response.choices[0]
            content = choice.message.content or ""

            return {
                "content": content,
                "model": self.model,
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
            logger.error(f"DeepSeek调用失败: {str(e)}")
            raise Exception(f"DeepSeek调用失败: {str(e)}")


class QwenLLMProvider(BaseAIProvider):
    """阿里千问LLM提供商"""

    def __init__(
        self,
        api_key: str,
        model: str,
        base_url: str = None,
    ):
        super().__init__(api_key, model, base_url)
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def generate(
        self,
        prompt: Union[str, List[Dict[str, str]]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
        **kwargs,
    ) -> str:
        """
        生成文本回复

        Args:
            prompt: 提示词或消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            top_p: top_p参数
            **kwargs: 其他参数

        Returns:
            生成的文本
        """
        try:
            # 处理提示词格式
            if isinstance(prompt, str):
                messages = [{"role": "user", "content": prompt}]
            else:
                messages = prompt

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                **kwargs,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            logger.error(f"千问LLM调用失败: {str(e)}")
            raise Exception(f"千问LLM调用失败: {str(e)}")

    def get_provider_type(self) -> AIProviderType:
        return AIProviderType.QWEN

    async def generate_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 0.9,
    ) -> Dict[str, Any]:
        """
        生成LLM回复（兼容现有适配器接口）

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
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
            )

            choice = response.choices[0]
            content = choice.message.content or ""

            return {
                "content": content,
                "model": self.model,
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
