"""
通义千问图像生成提供商实现
基于通义千问图像生成服务
"""

from typing import Any, Dict, List

import aiohttp
import dashscope
from app.core.config import settings
from app.core.logger import get_logger
from dashscope import ImageSynthesis

logger = get_logger("image_service")


class QwenImageProvider:
    """通义千问图像生成提供商"""

    SUPPORTED_SIZES: List[str] = [
        "1280*720",
        "1088*832",
        "960*960",
        "832*1088",
        "720*1280",
    ]

    SUPPORTED_QUALITIES: List[str] = ["standard", "hd"]

    SUPPORTED_STYLES: List[str] = [
        "realistic",  # 写实
        "anime",  # 动漫
        "oil_painting",  # 油画
        "watercolor",  # 水彩
        "sketch",  # 素描
    ]

    def __init__(self, model: str = "wan2.2-t2i-flash"):
        dashscope.base_http_api_url = "https://dashscope.aliyuncs.com/api/v1"
        dashscope.api_key = settings.QWEN_API_KEY
        self.model = model

    async def generate(
        self,
        prompt: str,
        size: str = "720*1280",
        quality: str = "standard",
        style: str = "realistic",
        **kwargs,
    ) -> bytes:
        """
        生成图像

        Args:
            prompt: 图像描述提示词
            size: 图像尺寸
            quality: 图像质量
            style: 图像风格

        Returns:
            图像字节数据
        """
        try:
            validated = self.validate_params(size=size, quality=quality, style=style)

            response = ImageSynthesis.call(
                model=self.model,
                prompt=prompt,
                n=1,
                size=validated["size"],
                quality=validated["quality"],
                style=validated["style"],
            )

            if response.status_code != 200:
                logger.error("API错误: %s - %s", response.code, response.message)
                raise RuntimeError("API错误")

            results = getattr(response.output, "results", [])
            if not results:
                logger.error("未返回图像结果")
                raise RuntimeError("未返回图像结果")

            image_url = results[0].url
            if not image_url:
                logger.error("未返回图像URL")
                raise RuntimeError("未返回图像URL")

            return await self._download_image(image_url)

        except Exception as e:
            logger.exception("通义千问图像生成失败")
            raise

    async def _download_image(self, url: str) -> bytes:
        """下载图像数据"""
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    logger.error("下载图像失败: HTTP %s", resp.status)
                    raise RuntimeError("下载图像失败")
                return await resp.read()

    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """验证并规范化图像生成参数"""
        validated = dict(kwargs)
        if "size" in validated and validated["size"] not in self.SUPPORTED_SIZES:
            logger.warning("无效尺寸 %s, 使用默认 1024*1024", validated["size"])
            validated["size"] = "1024*1024"

        if (
            "quality" in validated
            and validated["quality"] not in self.SUPPORTED_QUALITIES
        ):
            logger.warning("无效质量 %s, 使用默认 standard", validated["quality"])
            validated["quality"] = "standard"

        if "style" in validated and validated["style"] not in self.SUPPORTED_STYLES:
            logger.warning("无效风格 %s, 使用默认 realistic", validated["style"])
            validated["style"] = "realistic"

        return validated

    def get_supported_models(self) -> List[str]:
        return ["qwen-image", "wanx-v1", "wanx-v1-turbo"]

    def get_supported_sizes(self) -> List[str]:
        return self.SUPPORTED_SIZES

    def get_supported_styles(self) -> List[str]:
        return self.SUPPORTED_STYLES
