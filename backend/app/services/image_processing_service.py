"""
图片处理服务
"""

import io
import uuid
from typing import Dict, Any, Optional, Tuple
from PIL import Image, ImageOps
import logging

logger = logging.getLogger(__name__)


class ImageProcessingService:
    """图片处理服务类"""

    def __init__(self):
        self.supported_formats = ["JPEG", "PNG", "GIF", "WEBP", "BMP"]
        self.max_dimensions = (4096, 4096)
        self.thumbnail_size = (300, 300)

    async def process_image(
        self,
        file_content: bytes,
        file_name: str,
        compress: bool = True,
        max_width: int = 1920,
        max_height: int = 1080,
        quality: int = 85,
    ) -> Dict[str, Any]:
        """
        处理图片

        Args:
            file_content: 图片文件内容
            file_name: 文件名
            compress: 是否压缩
            max_width: 最大宽度
            max_height: 最大高度
            quality: 压缩质量

        Returns:
            处理后的图片信息
        """
        try:
            # 打开图片
            image = Image.open(io.BytesIO(file_content))

            # 获取图片信息
            width, height = image.size
            format_name = image.format or "JPEG"
            mime_type = f"image/{format_name.lower()}"

            # 验证图片格式
            if format_name not in self.supported_formats:
                raise ValueError(f"不支持的图片格式: {format_name}")

            # 验证图片尺寸
            if width > self.max_dimensions[0] or height > self.max_dimensions[1]:
                raise ValueError(f"图片尺寸过大: {width}x{height}")

            # 处理图片
            processed_image = image.copy()

            # 压缩和调整尺寸
            if compress:
                processed_image = await self._compress_image(
                    processed_image, max_width, max_height, quality
                )

            # 生成缩略图
            thumbnail = await self._generate_thumbnail(image)

            # 转换为字节
            compressed_data = await self._image_to_bytes(
                processed_image, format_name, quality
            )
            thumbnail_data = await self._image_to_bytes(thumbnail, "JPEG", 80)

            # 计算质量评分
            quality_score = await self._calculate_quality_score(image)

            # 生成新的文件名
            new_file_name = f"{uuid.uuid4().hex}.{format_name.lower()}"

            return {
                "file_name": new_file_name,
                "mime_type": mime_type,
                "width": processed_image.width,
                "height": processed_image.height,
                "format": format_name.lower(),
                "compressed_data": compressed_data,
                "thumbnail_data": thumbnail_data,
                "quality_score": quality_score,
                "metadata": {
                    "original_width": width,
                    "original_height": height,
                    "original_format": format_name,
                    "original_size": len(file_content),
                    "compressed_size": len(compressed_data),
                    "compression_ratio": len(compressed_data) / len(file_content),
                },
            }

        except Exception as e:
            logger.error(f"图片处理失败: {str(e)}")
            raise

    async def _compress_image(
        self,
        image: Image.Image,
        max_width: int,
        max_height: int,
        quality: int,
    ) -> Image.Image:
        """压缩图片"""
        try:
            # 计算新尺寸
            width, height = image.size

            if width <= max_width and height <= max_height:
                return image

            # 计算缩放比例
            width_ratio = max_width / width
            height_ratio = max_height / height
            ratio = min(width_ratio, height_ratio)

            new_width = int(width * ratio)
            new_height = int(height * ratio)

            # 调整尺寸
            compressed_image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )

            return compressed_image

        except Exception as e:
            logger.error(f"图片压缩失败: {str(e)}")
            raise

    async def _generate_thumbnail(
        self,
        image: Image.Image,
        size: Tuple[int, int] = (300, 300),
    ) -> Image.Image:
        """生成缩略图"""
        try:
            # 使用thumbnail方法保持宽高比
            thumbnail = image.copy()
            thumbnail.thumbnail(size, Image.Resampling.LANCZOS)

            # 创建正方形缩略图
            square_thumbnail = Image.new("RGB", size, (255, 255, 255))

            # 计算居中位置
            x = (size[0] - thumbnail.width) // 2
            y = (size[1] - thumbnail.height) // 2

            # 粘贴缩略图
            square_thumbnail.paste(thumbnail, (x, y))

            return square_thumbnail

        except Exception as e:
            logger.error(f"缩略图生成失败: {str(e)}")
            raise

    async def _image_to_bytes(
        self,
        image: Image.Image,
        format: str,
        quality: int = 85,
    ) -> bytes:
        """将图片转换为字节"""
        try:
            buffer = io.BytesIO()

            # 转换为RGB模式（如果需要）
            if format.upper() == "JPEG" and image.mode != "RGB":
                image = image.convert("RGB")

            # 保存图片
            image.save(buffer, format=format, quality=quality, optimize=True)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"图片转换失败: {str(e)}")
            raise

    async def _calculate_quality_score(self, image: Image.Image) -> float:
        """计算图片质量评分"""
        try:
            # 简单的质量评分算法
            width, height = image.size

            # 基于尺寸的评分
            size_score = min(1.0, (width * height) / (1920 * 1080))

            # 基于格式的评分
            format_score = 1.0
            if image.format == "JPEG":
                format_score = 0.9
            elif image.format == "PNG":
                format_score = 1.0
            elif image.format == "WEBP":
                format_score = 0.95

            # 综合评分
            quality_score = (size_score + format_score) / 2

            return round(quality_score, 2)

        except Exception as e:
            logger.error(f"质量评分计算失败: {str(e)}")
            return 0.5

    async def resize_image(
        self,
        image_data: bytes,
        width: int,
        height: int,
    ) -> bytes:
        """调整图片尺寸"""
        try:
            image = Image.open(io.BytesIO(image_data))
            resized_image = image.resize((width, height), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            resized_image.save(buffer, format=image.format or "JPEG", quality=85)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"图片尺寸调整失败: {str(e)}")
            raise

    async def convert_format(
        self,
        image_data: bytes,
        target_format: str,
        quality: int = 85,
    ) -> bytes:
        """转换图片格式"""
        try:
            image = Image.open(io.BytesIO(image_data))

            # 转换为RGB模式（如果需要）
            if target_format.upper() == "JPEG" and image.mode != "RGB":
                image = image.convert("RGB")

            buffer = io.BytesIO()
            image.save(buffer, format=target_format, quality=quality)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            logger.error(f"图片格式转换失败: {str(e)}")
            raise

    async def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """分析图片元数据"""
        try:
            image = Image.open(io.BytesIO(image_data))

            # 获取EXIF信息
            exif_data = {}
            if hasattr(image, "_getexif"):
                exif = image._getexif()
                if exif:
                    for tag, value in exif.items():
                        exif_data[tag] = str(value)

            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "size": len(image_data),
                "exif": exif_data,
            }

        except Exception as e:
            logger.error(f"图片分析失败: {str(e)}")
            return {}


# 创建服务实例
image_processing_service = ImageProcessingService()
