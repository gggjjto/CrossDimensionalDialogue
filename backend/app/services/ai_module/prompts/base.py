"""
提示词基类
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class PromptType(Enum):
    """提示词类型"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class BasePrompt(ABC):
    """提示词抽象基类"""

    def __init__(self, prompt_type: PromptType = PromptType.USER):
        """
        初始化提示词

        Args:
            prompt_type: 提示词类型
        """
        self.prompt_type = prompt_type

    @abstractmethod
    def build(self, **kwargs) -> str:
        """
        构建提示词

        Args:
            **kwargs: 提示词参数

        Returns:
            构建好的提示词字符串
        """
        pass

    def build_message(self, **kwargs) -> Dict[str, str]:
        """
        构建消息格式的提示词

        Args:
            **kwargs: 提示词参数

        Returns:
            消息格式的提示词字典
        """
        content = self.build(**kwargs)
        return {"role": self.prompt_type.value, "content": content}

    def get_prompt_type(self) -> PromptType:
        """
        获取提示词类型

        Returns:
            提示词类型
        """
        return self.prompt_type
