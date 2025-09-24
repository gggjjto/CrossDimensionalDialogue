"""
AI模型提供商基类
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)


class AIProviderType(Enum):
    """AI提供商类型"""

    DEEPSEEK = "deepseek"
    QWEN = "qwen"
    ALIYUN = "aliyun"


class BaseAIProvider(ABC):
    """AI模型提供商基类"""

    def __init__(
        self, api_key: str, model: str, base_url: Optional[str] = None, **kwargs
    ):
        """
        初始化提供商

        Args:
            api_key: API密钥
            model: 模型名称
            base_url: API基础URL（可选）
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.kwargs = kwargs

        # 验证必需参数
        if not api_key:
            raise ValueError("API密钥不能为空")
        if not model:
            raise ValueError("模型名称不能为空")

    @abstractmethod
    async def generate(
        self, prompt: Union[str, List[Dict[str, str]]], **kwargs
    ) -> Union[str, bytes, List[float]]:
        """
        生成内容

        Args:
            prompt: 提示词（字符串或消息列表）
            **kwargs: 其他参数

        Returns:
            生成的内容（文本、图像字节或向量）
        """
        pass

    @abstractmethod
    def get_provider_type(self) -> AIProviderType:
        """
        获取提供商类型

        Returns:
            提供商类型
        """
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        return {
            "provider": self.get_provider_type().value,
            "model": self.model,
            "base_url": self.base_url or "default",
        }

    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """
        验证和清理参数

        Args:
            **kwargs: 输入参数

        Returns:
            验证后的参数
        """
        # 子类可以重写此方法进行特定验证
        return kwargs

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            是否健康
        """
        try:
            # 简单的测试调用
            await self.generate("test", max_tokens=1)
            return True
        except Exception as e:
            logger.error(f"Provider health check failed: {str(e)}")
            return False
