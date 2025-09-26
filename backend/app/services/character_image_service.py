"""
角色形象图片生成服务

支持用户上传图片或使用AI生成角色形象图片
"""

import io
from typing import Dict, Optional

import httpx
from app.core.config import settings
from app.core.logger import get_logger
from app.models.character import Character
from app.services.image_service import QwenImageProvider
from PIL import Image

logger = get_logger("character_image_service")


class CharacterImageService:
    """角色形象图片生成服务"""

    def __init__(self):
        self.provider = QwenImageProvider(model=settings.QWEN_IMAGE_MODEL)

    async def generate_character_image(
        self, character: Character, style: str = "realistic", size: str = "720*1280"
    ) -> Optional[bytes]:
        """
        为角色生成AI形象图片

        Args:
            character: 角色对象
            style: 图片风格 (realistic, anime, cartoon, artistic)
            size: 图片尺寸 (1024*1024, 1024*768, 768*1024)

        Returns:
            生成的图片字节数据或None
        """
        try:
            # 构建 prompt
            prompt = self._build_image_prompt(character, style)

            # 调用图像生成 provider
            image_bytes = await self.provider.generate(
                prompt=prompt,
                size=size,
                style=style,
                quality="standard",
            )

            if image_bytes:
                logger.info(f"成功为角色 {character.name} 生成AI形象图片")
                return image_bytes
            else:
                logger.warning(f"为角色 {character.name} 生成AI形象图片失败")
                return None

        except Exception as e:
            logger.error(f"生成角色形象图片时发生错误: {str(e)}")
            return None

    async def generate_character_image_with_prompt(
        self,
        prompt: str,
        size: str = "720*1280",
        style: str = "realistic",
        quality: str = "standard",
    ) -> Optional[bytes]:
        """
        使用提示词生成角色形象图片

        Args:
            prompt: 提示词
            size: 图片尺寸
            style: 图片风格
            quality: 图片质量
        Returns:
            生成的图片字节数据或None
        """
        try:
            image_bytes = await self.provider.generate(
                prompt=prompt,
                size=size,
                quality=quality,
                style=style,
            )

            if image_bytes:
                logger.info(f"成功使用提示词生成角色形象图片")
                return image_bytes
        except Exception as e:
            logger.error(f"使用提示词生成角色形象图片时发生错误: {str(e)}")
            return None

    def _build_image_prompt(self, character: Character, style: str) -> str:
        """
        构建图片生成提示词（中文版本）
        """
        base_prompt = f"一幅{style}风格的{character.name}肖像"

        # 添加角色简介
        if character.short_bio:
            base_prompt += f"，{character.short_bio}"

        # 添加人格特征
        if character.persona_text:
            base_prompt += f"，性格特点：{character.persona_text}"

        # 风格修饰词（中文化）
        style_modifiers = {
            "realistic": "写实，高清，细节丰富，专业摄影效果",
            "anime": "动漫风格，色彩鲜艳，细节清晰",
            "cartoon": "卡通风格，简洁，夸张，明亮",
            "artistic": "艺术风格，油画感，创意十足，优雅",
        }
        if style in style_modifiers:
            base_prompt += f"，{style_modifiers[style]}"

        # 通用修饰
        base_prompt += "，高质量，构图居中，光线自然"

        return base_prompt

    async def validate_image(self, image_bytes: bytes) -> bool:
        """验证生成的图片是否有效"""
        try:
            img = Image.open(io.BytesIO(image_bytes))
            img.verify()
            return True
        except Exception as e:
            logger.error(f"验证图片失败: {str(e)}")
            return False

    async def download_and_validate_image(self, image_url: str) -> Optional[bytes]:
        """
        下载并验证图片

        Args:
            image_url: 图片URL

        Returns:
            图片字节数据或None
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(image_url)

                if response.status_code == 200:
                    # 验证是否为有效图片
                    try:
                        image = Image.open(io.BytesIO(response.content))
                        image.verify()  # 验证图片格式
                        return response.content
                    except Exception as e:
                        logger.error(f"图片验证失败: {str(e)}")
                        return None
                else:
                    logger.error(f"下载图片失败: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"下载图片时发生错误: {str(e)}")
            return None

    def get_supported_styles(self) -> Dict[str, str]:
        """
        获取支持的图片风格

        Returns:
            风格字典
        """
        return {
            "realistic": "写实风格",
            "anime": "动漫风格",
            "cartoon": "卡通风格",
            "artistic": "艺术风格",
        }

    def get_supported_sizes(self) -> Dict[str, str]:
        return {s: s for s in self.provider.get_supported_sizes()}


# 全局服务实例
character_image_service = CharacterImageService()
