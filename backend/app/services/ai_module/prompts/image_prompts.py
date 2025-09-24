"""
文生图提示词
"""

from typing import Optional, List, Dict, Any
from .base import BasePrompt, PromptType


class CharacterImagePrompt(BasePrompt):
    """角色图像生成提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        character_description: str,
        style: str = "anime",
        quality: str = "high",
        aspect_ratio: str = "1:1",
        additional_details: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建角色图像生成提示词

        Args:
            character_description: 角色描述
            style: 风格（anime, realistic, cartoon等）
            quality: 质量（high, medium, low）
            aspect_ratio: 宽高比（1:1, 16:9, 9:16等）
            additional_details: 额外细节（可选）
            **kwargs: 其他参数

        Returns:
            图像生成提示词
        """
        prompt_parts = [
            f"生成一个 {style} 风格的图片，角色描述：{character_description}"
        ]

        if additional_details:
            prompt_parts.append(f"额外细节：{additional_details}")

        # 添加质量和风格要求
        quality_terms = {
            "high": "high quality, detailed, professional",
            "medium": "good quality, clear",
            "low": "simple, clean",
        }

        style_terms = {
            "anime": "anime style, manga style, Japanese animation",
            "realistic": "photorealistic, realistic, detailed",
            "cartoon": "cartoon style, colorful, stylized",
            "fantasy": "fantasy art, magical, mystical",
            "sci-fi": "sci-fi, futuristic, technological",
        }

        prompt_parts.append(quality_terms.get(quality, "good quality"))
        prompt_parts.append(style_terms.get(style, "anime style"))

        # 添加宽高比要求
        if aspect_ratio != "1:1":
            prompt_parts.append(f"Aspect ratio: {aspect_ratio}")

        return ", ".join(prompt_parts)


class GeneralImagePrompt(BasePrompt):
    """通用图像生成提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        description: str,
        style: str = "realistic",
        mood: Optional[str] = None,
        composition: Optional[str] = None,
        lighting: Optional[str] = None,
        **kwargs,
    ) -> str:
        """
        构建通用图像生成提示词

        Args:
            description: 图像描述
            style: 风格
            mood: 情绪/氛围（可选）
            composition: 构图（可选）
            lighting: 光照（可选）
            **kwargs: 其他参数

        Returns:
            图像生成提示词
        """
        prompt_parts = [description]

        if style:
            prompt_parts.append(f"Style: {style}")

        if mood:
            prompt_parts.append(f"Mood: {mood}")

        if composition:
            prompt_parts.append(f"Composition: {composition}")

        if lighting:
            prompt_parts.append(f"Lighting: {lighting}")

        return ", ".join(prompt_parts)


class SceneImagePrompt(BasePrompt):
    """场景图像生成提示词"""

    def __init__(self):
        super().__init__(PromptType.USER)

    def build(
        self,
        scene_description: str,
        environment: str,
        time_of_day: Optional[str] = None,
        weather: Optional[str] = None,
        characters: Optional[List[str]] = None,
        **kwargs,
    ) -> str:
        """
        构建场景图像生成提示词

        Args:
            scene_description: 场景描述
            environment: 环境（室内/室外/城市/自然等）
            time_of_day: 时间（白天/夜晚/黄昏等）
            weather: 天气（晴天/雨天/雪天等）
            characters: 角色列表（可选）
            **kwargs: 其他参数

        Returns:
            场景图像生成提示词
        """
        prompt_parts = [
            f"Scene: {scene_description}",
            f"Environment: {environment}",
        ]

        if time_of_day:
            prompt_parts.append(f"Time: {time_of_day}")

        if weather:
            prompt_parts.append(f"Weather: {weather}")

        if characters:
            prompt_parts.append(f"Characters: {', '.join(characters)}")

        return ", ".join(prompt_parts)
