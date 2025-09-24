"""
通义千问图像生成提供商实现
基于通义千问图像生成服务
"""

import logging
from typing import Dict, Any, Optional
import dashscope
from dashscope import ImageSynthesis

from .base import BaseAIProvider, AIProviderType

logger = logging.getLogger(__name__)


class QwenImageProvider(BaseAIProvider):
    """通义千问图像生成提供商"""

    def __init__(self, api_key: str, model: str = "qwen-image", base_url: str = None):
        super().__init__(api_key, model, base_url)
        # 设置API密钥
        dashscope.api_key = api_key

    async def generate(
        self,
        prompt: str,
        size: str = "1024*1024",
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
            **kwargs: 其他参数

        Returns:
            图像字节数据
        """
        try:
            # 调用通义千问图像生成API
            response = ImageSynthesis.call(
                model=self.model,
                prompt=prompt,
                n=1,
                size=size,
                quality=quality,
                style=style,
            )

            if response.status_code == 200:
                # 检查是否有结果
                if not response.output.results or len(response.output.results) == 0:
                    logger.error(f"图像生成失败：未返回结果: {response.output.results}")
                    raise Exception("图像生成失败：未返回结果")

                # 获取生成的图像URL
                image_url = response.output.results[0].url
                if not image_url:
                    raise Exception("图像生成失败：未返回图像URL")

                # 下载图像
                import aiohttp

                async with aiohttp.ClientSession() as session:
                    async with session.get(image_url) as resp:
                        if resp.status == 200:
                            return await resp.read()
                        else:
                            raise Exception(f"下载图像失败：HTTP {resp.status}")
            else:
                error_msg = (
                    f"通义千问图像生成API错误: {response.code} - {response.message}"
                )
                logger.error(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            logger.error(f"通义千问图像生成失败: {str(e)}")
            raise Exception(f"通义千问图像生成失败: {str(e)}")

    def get_provider_type(self) -> AIProviderType:
        return AIProviderType.QWEN

    def validate_params(self, **kwargs) -> Dict[str, Any]:
        """验证图像生成参数"""
        validated = super().validate_params(**kwargs)

        # 验证尺寸
        valid_sizes = [
            "1024*1024",
            "1024*768",
            "768*1024",
            "1280*720",
            "720*1280",
            "1024*576",
            "576*1024",
        ]
        if "size" in validated and validated["size"] not in valid_sizes:
            logger.warning(f"无效的图像尺寸: {validated['size']}, 使用默认尺寸")
            validated["size"] = "1024*1024"

        # 验证质量
        valid_qualities = ["standard", "hd"]
        if "quality" in validated and validated["quality"] not in valid_qualities:
            logger.warning(f"无效的图像质量: {validated['quality']}, 使用默认质量")
            validated["quality"] = "standard"

        # 验证风格
        valid_styles = ["realistic", "anime", "oil_painting", "watercolor", "sketch"]
        if "style" in validated and validated["style"] not in valid_styles:
            logger.warning(f"无效的图像风格: {validated['style']}, 使用默认风格")
            validated["style"] = "realistic"

        return validated

    def get_supported_models(self) -> list[str]:
        """获取支持的模型列表"""
        return [
            "qwen-image",  # 通义千问图像生成
            "wanx-v1",  # 通义万相1.0
            "wanx-v1-turbo",  # 通义万相1.0 Turbo
        ]

    def get_supported_sizes(self) -> list[str]:
        """获取支持的尺寸列表"""
        return [
            "1024*1024",
            "1024*768",
            "768*1024",
            "1280*720",
            "720*1280",
            "1024*576",
            "576*1024",
        ]

    def get_supported_styles(self) -> list[str]:
        """获取支持的风格列表"""
        return [
            "realistic",  # 写实
            "anime",  # 动漫
            "oil_painting",  # 油画
            "watercolor",  # 水彩
            "sketch",  # 素描
        ]
