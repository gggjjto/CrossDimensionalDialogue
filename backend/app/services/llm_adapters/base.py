"""
LLM模型适配器基类
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMAdapter(ABC):
    """LLM模型适配器基类"""

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
