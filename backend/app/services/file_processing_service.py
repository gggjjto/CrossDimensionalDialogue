"""
文件处理服务
"""

import hashlib
import mimetypes
import uuid
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FileProcessingService:
    """文件处理服务类"""

    def __init__(self):
        self.allowed_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".txt",
            ".rtf",
            ".zip",
            ".rar",
            ".7z",
            ".tar",
            ".gz",
            ".mp4",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".mp3",
            ".wav",
            ".flac",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
        }

        self.file_type_mapping = {
            ".pdf": "document",
            ".doc": "document",
            ".docx": "document",
            ".xls": "document",
            ".xlsx": "document",
            ".ppt": "document",
            ".pptx": "document",
            ".txt": "document",
            ".rtf": "document",
            ".zip": "archive",
            ".rar": "archive",
            ".7z": "archive",
            ".tar": "archive",
            ".gz": "archive",
            ".mp4": "video",
            ".avi": "video",
            ".mov": "video",
            ".wmv": "video",
            ".flv": "video",
            ".mp3": "audio",
            ".wav": "audio",
            ".flac": "audio",
            ".jpg": "image",
            ".jpeg": "image",
            ".png": "image",
            ".gif": "image",
            ".bmp": "image",
            ".webp": "image",
        }

    async def process_file(
        self,
        file_content: bytes,
        file_name: str,
        scan_security: bool = True,
    ) -> Dict[str, Any]:
        """
        处理文件

        Args:
            file_content: 文件内容
            file_name: 文件名
            scan_security: 是否进行安全扫描

        Returns:
            处理后的文件信息
        """
        try:
            # 获取文件扩展名
            file_extension = self._get_file_extension(file_name)

            # 验证文件类型
            if file_extension not in self.allowed_extensions:
                raise ValueError(f"不支持的文件类型: {file_extension}")

            # 获取MIME类型
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = "application/octet-stream"

            # 确定文件类型
            file_type = self.file_type_mapping.get(file_extension, "other")

            # 计算校验和
            checksum = await self._calculate_checksum(file_content)

            # 安全扫描
            security_status = "safe"
            if scan_security:
                security_status = await self._scan_file_security(
                    file_content, file_name
                )

            # 生成预览（如果支持）
            preview_data = None
            if file_type in ["image", "document"]:
                preview_data = await self._generate_preview(file_content, file_type)

            # 生成新的文件名
            new_file_name = f"{uuid.uuid4().hex}{file_extension}"

            return {
                "file_name": new_file_name,
                "mime_type": mime_type,
                "file_extension": file_extension,
                "file_type": file_type,
                "checksum": checksum,
                "security_status": security_status,
                "preview_data": preview_data,
                "metadata": {
                    "original_name": file_name,
                    "original_size": len(file_content),
                    "file_type": file_type,
                },
            }

        except Exception as e:
            logger.error(f"文件处理失败: {str(e)}")
            raise

    def _get_file_extension(self, file_name: str) -> str:
        """获取文件扩展名"""
        if "." not in file_name:
            return ""

        extension = file_name.lower().split(".")[-1]
        return f".{extension}"

    async def _calculate_checksum(self, file_content: bytes) -> str:
        """计算文件校验和"""
        try:
            sha256_hash = hashlib.sha256()
            sha256_hash.update(file_content)
            return f"sha256:{sha256_hash.hexdigest()}"
        except Exception as e:
            logger.error(f"校验和计算失败: {str(e)}")
            return ""

    async def _scan_file_security(
        self,
        file_content: bytes,
        file_name: str,
    ) -> str:
        """
        文件安全扫描

        Args:
            file_content: 文件内容
            file_name: 文件名

        Returns:
            安全状态: safe, unsafe, failed
        """
        try:
            # 检查文件大小
            if len(file_content) > 50 * 1024 * 1024:  # 50MB
                logger.warning(f"文件过大，跳过安全扫描: {file_name}")
                return "safe"

            # 检查文件头
            if not await self._check_file_header(file_content, file_name):
                logger.warning(f"文件头检查失败: {file_name}")
                return "unsafe"

            # 检查恶意内容
            if await self._check_malicious_content(file_content):
                logger.warning(f"检测到恶意内容: {file_name}")
                return "unsafe"

            return "safe"

        except Exception as e:
            logger.error(f"安全扫描失败: {str(e)}")
            return "failed"

    async def _check_file_header(self, file_content: bytes, file_name: str) -> bool:
        """检查文件头"""
        try:
            if len(file_content) < 4:
                return False

            # 常见文件头签名
            file_signatures = {
                b"\x89PNG\r\n\x1a\n": [".png"],
                b"\xff\xd8\xff": [".jpg", ".jpeg"],
                b"GIF87a": [".gif"],
                b"GIF89a": [".gif"],
                b"RIFF": [".wav", ".avi"],
                b"PK\x03\x04": [".zip", ".docx", ".xlsx", ".pptx"],
                b"%PDF": [".pdf"],
                b"\x00\x00\x01\x00": [".ico"],
                b"BM": [".bmp"],
            }

            # 检查文件头
            for signature, extensions in file_signatures.items():
                if file_content.startswith(signature):
                    file_extension = self._get_file_extension(file_name)
                    if file_extension in extensions:
                        return True

            # 如果没有匹配的签名，检查是否为文本文件
            try:
                file_content[:100].decode("utf-8")
                return True
            except UnicodeDecodeError:
                pass

            return True  # 默认允许

        except Exception as e:
            logger.error(f"文件头检查失败: {str(e)}")
            return False

    async def _check_malicious_content(self, file_content: bytes) -> bool:
        """检查恶意内容"""
        try:
            # 检查常见的恶意代码模式
            malicious_patterns = [
                b"<script",
                b"javascript:",
                b"eval(",
                b"exec(",
                b"system(",
                b"cmd.exe",
                b"powershell",
                b"bash",
            ]

            content_lower = file_content.lower()
            for pattern in malicious_patterns:
                if pattern in content_lower:
                    return True

            return False

        except Exception as e:
            logger.error(f"恶意内容检查失败: {str(e)}")
            return False

    async def _generate_preview(
        self,
        file_content: bytes,
        file_type: str,
    ) -> Optional[bytes]:
        """生成文件预览"""
        try:
            if file_type == "image":
                # 对于图片，生成缩略图
                from app.services.image_processing_service import (
                    image_processing_service,
                )

                thumbnail_data = await image_processing_service._generate_thumbnail(
                    image_processing_service._open_image(file_content)
                )
                return await image_processing_service._image_to_bytes(
                    thumbnail_data, "JPEG", 80
                )

            elif file_type == "document":
                # 对于文档，生成预览图片（需要额外的库支持）
                # 这里可以集成PDF预览、Office文档预览等
                return None

            return None

        except Exception as e:
            logger.error(f"预览生成失败: {str(e)}")
            return None

    async def get_file_info(
        self, file_content: bytes, file_name: str
    ) -> Dict[str, Any]:
        """获取文件信息"""
        try:
            file_extension = self._get_file_extension(file_name)
            mime_type, _ = mimetypes.guess_type(file_name)
            file_type = self.file_type_mapping.get(file_extension, "other")

            return {
                "name": file_name,
                "extension": file_extension,
                "mime_type": mime_type or "application/octet-stream",
                "type": file_type,
                "size": len(file_content),
                "checksum": await self._calculate_checksum(file_content),
            }

        except Exception as e:
            logger.error(f"文件信息获取失败: {str(e)}")
            return {}


# 创建服务实例
file_processing_service = FileProcessingService()
