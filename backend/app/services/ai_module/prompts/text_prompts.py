"""
文生文提示词
"""

from typing import Optional, List, Dict, Any
from .base import BasePrompt, PromptType


class CharacterSystemPrompt(BasePrompt):
    """角色系统提示词"""

    def __init__(self):
        super().__init__(PromptType.SYSTEM)

    def build(
        self,
        character_name: str,
        character_description: str,
        personality: str,
        background: str,
        speaking_style: str,
        knowledge_base: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建角色系统提示词

        Args:
            character_name: 角色名称
            character_description: 角色描述
            personality: 性格特点
            background: 背景故事
            speaking_style: 说话风格
            knowledge_base: 知识库内容（可选）
            **kwargs: 其他参数

        Returns:
            系统提示词
        """
        prompt_parts = [
            f"你是{character_name}，一个虚拟角色。",
            f"角色描述：{character_description}",
            f"性格特点：{personality}",
            f"背景故事：{background}",
            f"说话风格：{speaking_style}",
        ]

        if knowledge_base:
            prompt_parts.append(f"相关知识：{knowledge_base}")

        prompt_parts.extend(
            [
                "",
                "请严格按照以上设定来扮演这个角色，保持角色的一致性和真实性。",
                "在对话中要体现出角色的性格特点和说话风格。",
                "如果遇到不确定的问题，可以基于角色的背景和性格进行合理的推测。",
            ]
        )

        return "\n".join(prompt_parts)


class CharacterDialoguePrompt(BasePrompt):
    """角色对话提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建角色对话提示词

        Args:
            user_message: 用户消息
            conversation_history: 对话历史（可选）
            context: 上下文信息（可选）
            **kwargs: 其他参数

        Returns:
            对话提示词
        """
        prompt_parts = []

        if context:
            prompt_parts.append(f"上下文：{context}")

        if conversation_history:
            prompt_parts.append("对话历史：")
            for msg in conversation_history[-5:]:  # 只保留最近5条历史
                role = "用户" if msg["role"] == "user" else "你"
                prompt_parts.append(f"{role}：{msg['content']}")

        prompt_parts.append(f"用户：{user_message}")
        prompt_parts.append("请以角色的身份回复：")

        return "\n".join(prompt_parts)


class GeneralTextPrompt(BasePrompt):
    """通用文本提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        task: str,
        content: str,
        style: Optional[str] = None,
        length: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建通用文本提示词

        Args:
            task: 任务描述
            content: 内容
            style: 风格（可选）
            length: 长度要求（可选）
            **kwargs: 其他参数

        Returns:
            通用提示词
        """
        prompt_parts = [f"任务：{task}"]

        if style:
            prompt_parts.append(f"风格：{style}")

        if length:
            prompt_parts.append(f"长度：{length}")

        prompt_parts.append(f"内容：{content}")

        return "\n".join(prompt_parts)


class RAGPrompt(BasePrompt):
    """RAG检索增强生成提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        question: str,
        retrieved_docs: List[str],
        context: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建RAG提示词

        Args:
            question: 问题
            retrieved_docs: 检索到的文档
            context: 上下文（可选）
            **kwargs: 其他参数

        Returns:
            RAG提示词
        """
        prompt_parts = []

        if context:
            prompt_parts.append(f"上下文：{context}")

        prompt_parts.append("相关文档：")
        for i, doc in enumerate(retrieved_docs, 1):
            prompt_parts.append(f"{i}. {doc}")

        prompt_parts.extend(
            [
                "",
                f"问题：{question}",
                "",
                "请基于以上相关文档回答问题，如果文档中没有相关信息，请明确说明。",
            ]
        )

        return "\n".join(prompt_parts)
