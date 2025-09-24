"""
图生文提示词
"""

from typing import Optional, List, Dict, Any
from .base import BasePrompt, PromptType


class ImageAnalysisPrompt(BasePrompt):
    """图像分析提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        analysis_type: str = "general",
        focus_areas: Optional[List[str]] = None,
        detail_level: str = "medium",
        **kwargs,
    ) -> str:
        """
        构建图像分析提示词

        Args:
            analysis_type: 分析类型（general, character, scene, object等）
            focus_areas: 关注区域（可选）
            detail_level: 详细程度（low, medium, high）
            **kwargs: 其他参数

        Returns:
            图像分析提示词
        """
        prompt_parts = []

        if analysis_type == "character":
            prompt_parts.append("请分析这张图片中的角色：")
            prompt_parts.extend(
                [
                    "- 外观特征（发型、服装、表情等）",
                    "- 性格特点推测",
                    "- 可能的背景故事",
                    "- 整体印象",
                ]
            )
        elif analysis_type == "scene":
            prompt_parts.append("请分析这张图片中的场景：")
            prompt_parts.extend(
                ["- 环境描述", "- 氛围和情绪", "- 构图和色彩", "- 可能的故事情节"]
            )
        elif analysis_type == "object":
            prompt_parts.append("请分析这张图片中的物体：")
            prompt_parts.extend(
                ["- 物体识别", "- 功能和用途", "- 材质和特征", "- 相关背景"]
            )
        else:  # general
            prompt_parts.append("请详细描述这张图片：")
            prompt_parts.extend(
                ["- 主要内容", "- 视觉元素", "- 色彩和构图", "- 整体印象"]
            )

        if focus_areas:
            prompt_parts.append(f"特别关注：{', '.join(focus_areas)}")

        detail_instructions = {
            "low": "简要描述即可",
            "medium": "提供中等详细程度的描述",
            "high": "提供非常详细的描述",
        }

        prompt_parts.append(
            detail_instructions.get(detail_level, "提供中等详细程度的描述")
        )

        return "\n".join(prompt_parts)


class ImageDescriptionPrompt(BasePrompt):
    """图像描述提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        description_style: str = "narrative",
        include_emotions: bool = True,
        include_colors: bool = True,
        include_composition: bool = False,
        **kwargs,
    ) -> str:
        """
        构建图像描述提示词

        Args:
            description_style: 描述风格（narrative, technical, poetic）
            include_emotions: 是否包含情感描述
            include_colors: 是否包含色彩描述
            include_composition: 是否包含构图描述
            **kwargs: 其他参数

        Returns:
            图像描述提示词
        """
        prompt_parts = []

        if description_style == "narrative":
            prompt_parts.append("请以叙述的方式描述这张图片，就像在讲故事一样。")
        elif description_style == "technical":
            prompt_parts.append("请以技术性的方式描述这张图片，注重客观事实。")
        elif description_style == "poetic":
            prompt_parts.append("请以诗意的语言描述这张图片，注重美感和意境。")

        requirements = []

        if include_emotions:
            requirements.append("情感和氛围")

        if include_colors:
            requirements.append("色彩和光影")

        if include_composition:
            requirements.append("构图和布局")

        if requirements:
            prompt_parts.append(f"请特别关注：{', '.join(requirements)}")

        return "\n".join(prompt_parts)


class ImageToTextPrompt(BasePrompt):
    """图像转文本提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self, task: str, output_format: str = "text", language: str = "中文", **kwargs
    ) -> str:
        """
        构建图像转文本提示词

        Args:
            task: 任务描述（提取文字、描述内容、分析等）
            output_format: 输出格式（text, json, markdown等）
            language: 输出语言
            **kwargs: 其他参数

        Returns:
            图像转文本提示词
        """
        prompt_parts = [
            f"任务：{task}",
            f"输出语言：{language}",
        ]

        if output_format == "json":
            prompt_parts.append("请以JSON格式输出结果")
        elif output_format == "markdown":
            prompt_parts.append("请以Markdown格式输出结果")
        else:
            prompt_parts.append("请以纯文本格式输出结果")

        return "\n".join(prompt_parts)
