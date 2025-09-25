"""
七牛云存储服务

提供高级存储功能，包括文件管理、图片处理等
"""

import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from app.core.config import settings
from app.utils.qiniu_storage import QiniuStorageClient, QiniuStorageError


class QiniuStorageService:
    """七牛云存储服务"""

    def __init__(self):
        """初始化存储服务"""
        self.client = QiniuStorageClient()
        self.bucket_name = settings.QINIU_BUCKET_NAME

    def upload_audio_file(
        self,
        file_path: Union[str, Path],
        user_id: int,
        conversation_id: Optional[int] = None,
        file_type: str = "audio",
    ) -> Dict[str, Any]:
        """
        上传音频文件

        Args:
            file_path: 本地文件路径
            user_id: 用户ID
            conversation_id: 对话ID（可选）
            file_type: 文件类型

        Returns:
            Dict: 上传结果信息
        """
        file_path = Path(file_path)

        # 验证文件类型
        if not self._is_audio_file(file_path):
            raise QiniuStorageError(f"不支持的文件类型: {file_path.suffix}")

        # 验证文件大小
        if file_path.stat().st_size > settings.MAX_AUDIO_FILE_SIZE:
            raise QiniuStorageError(
                f"文件过大，最大支持 {settings.MAX_AUDIO_FILE_SIZE // (1024*1024)}MB"
            )

        # 生成文件key
        prefix = f"audio/{user_id}"
        if conversation_id:
            prefix += f"/conversation/{conversation_id}"

        key = self.client._generate_file_key(str(file_path), prefix)

        # 上传文件
        result = self.client.upload_file(file_path, key, overwrite=True)

        return {
            **result,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "file_type": file_type,
            "original_name": file_path.name,
            "file_size": file_path.stat().st_size,
        }

    def upload_image_file(
        self,
        file_path: Union[str, Path],
        user_id: int,
        category: str = "general",
        file_type: str = "image",
    ) -> Dict[str, Any]:
        """
        上传图片文件

        Args:
            file_path: 本地文件路径
            user_id: 用户ID
            category: 图片分类
            file_type: 文件类型

        Returns:
            Dict: 上传结果信息
        """
        file_path = Path(file_path)

        # 验证文件类型
        if not self._is_image_file(file_path):
            raise QiniuStorageError(f"不支持的图片类型: {file_path.suffix}")

        # 生成文件key
        prefix = f"images/{user_id}/{category}"
        key = self.client._generate_file_key(str(file_path), prefix)

        # 上传文件
        result = self.client.upload_file(file_path, key, overwrite=True)

        return {
            **result,
            "user_id": user_id,
            "category": category,
            "file_type": file_type,
            "original_name": file_path.name,
            "file_size": file_path.stat().st_size,
        }

    def upload_character_avatar(
        self, file_path: Union[str, Path], character_id: int, file_type: str = "avatar"
    ) -> Dict[str, Any]:
        """
        上传角色头像

        Args:
            file_path: 本地文件路径
            character_id: 角色ID
            file_type: 文件类型

        Returns:
            Dict: 上传结果信息
        """
        file_path = Path(file_path)

        # 验证文件类型
        if not self._is_image_file(file_path):
            raise QiniuStorageError(f"不支持的图片类型: {file_path.suffix}")

        # 生成文件key
        prefix = f"characters/{character_id}/avatar"
        key = self.client._generate_file_key(str(file_path), prefix)

        # 上传文件
        result = self.client.upload_file(file_path, key, overwrite=True)

        return {
            **result,
            "character_id": character_id,
            "file_type": file_type,
            "original_name": file_path.name,
            "file_size": file_path.stat().st_size,
        }

    def upload_character_avatar_bytes(
        self, image_bytes: bytes, character_id: int, file_extension: str = "png"
    ) -> Dict[str, Any]:
        """
        上传角色头像（字节数据）

        Args:
            image_bytes: 图片字节数据
            character_id: 角色ID
            file_extension: 文件扩展名

        Returns:
            Dict: 上传结果信息
        """
        # 生成文件key
        prefix = f"characters/{character_id}/avatar"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{prefix}/{timestamp}.{file_extension}"

        # 确定内容类型
        content_type = mimetypes.guess_type(f"image.{file_extension}")[0] or "image/png"

        # 上传数据
        result = self.client.upload_data(
            image_bytes, key, content_type=content_type, overwrite=True
        )

        return {
            **result,
            "character_id": character_id,
            "file_type": "avatar",
        }

    def upload_document(
        self,
        file_path: Union[str, Path],
        user_id: int,
        document_type: str = "general",
        file_type: str = "document",
    ) -> Dict[str, Any]:
        """
        上传文档文件

        Args:
            file_path: 本地文件路径
            user_id: 用户ID
            document_type: 文档类型
            file_type: 文件类型

        Returns:
            Dict: 上传结果信息
        """
        file_path = Path(file_path)

        # 验证文件类型
        if not self._is_document_file(file_path):
            raise QiniuStorageError(f"不支持的文档类型: {file_path.suffix}")

        # 生成文件key
        prefix = f"documents/{user_id}/{document_type}"
        key = self.client._generate_file_key(str(file_path), prefix)

        # 上传文件
        result = self.client.upload_file(file_path, key, overwrite=True)

        return {
            **result,
            "user_id": user_id,
            "document_type": document_type,
            "file_type": file_type,
            "original_name": file_path.name,
            "file_size": file_path.stat().st_size,
        }

    def delete_user_files(
        self, user_id: int, file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        删除用户的所有文件

        Args:
            user_id: 用户ID
            file_type: 文件类型过滤（可选）

        Returns:
            Dict: 删除结果
        """
        prefix = f"audio/{user_id}"
        if file_type == "image":
            prefix = f"images/{user_id}"
        elif file_type == "document":
            prefix = f"documents/{user_id}"

        # 获取文件列表
        files_info = self.client.list_files(prefix=prefix)
        keys = [item["key"] for item in files_info.get("items", [])]

        if not keys:
            return {
                "success": True,
                "deleted_count": 0,
                "message": "没有找到要删除的文件",
            }

        # 批量删除
        result = self.client.delete_files(keys)

        return {
            **result,
            "deleted_count": len(keys),
            "user_id": user_id,
            "file_type": file_type,
        }

    def get_file_url(self, key: str, private: bool = False, expires: int = 3600) -> str:
        """
        获取文件访问URL

        Args:
            key: 文件key
            private: 是否使用私有URL
            expires: 私有URL过期时间（秒）

        Returns:
            str: 文件访问URL
        """
        if private:
            return self.client._get_private_url(key, expires)
        return self.client._get_public_url(key)

    def get_image_thumbnail_url(
        self,
        key: str,
        width: int = 200,
        height: int = 200,
        quality: int = 80,
        format: str = "jpg",
    ) -> str:
        """
        获取图片缩略图URL

        Args:
            key: 图片key
            width: 宽度
            height: 高度
            quality: 质量（1-100）
            format: 输出格式

        Returns:
            str: 缩略图URL
        """
        # 七牛云图片处理参数
        params = f"imageView2/1/w/{width}/h/{height}/q/{quality}/format/{format}"
        return self.client.get_image_url_with_params(key, params)

    def get_image_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取图片信息

        Args:
            key: 图片key

        Returns:
            Optional[Dict]: 图片信息
        """
        base_url = self.client._get_public_url(key)
        # 七牛云图片信息接口
        info_url = base_url + "?imageInfo"

        # 这里可以添加HTTP请求获取图片信息
        # 为了简化，直接返回基本信息
        file_info = self.client.get_file_info(key)
        if file_info:
            return {
                "key": key,
                "url": base_url,
                "size": file_info.get("fsize"),
                "mime_type": file_info.get("mimeType"),
                "created_at": datetime.fromtimestamp(
                    file_info.get("putTime", 0) / 10000000
                ),
            }
        return None

    def _is_audio_file(self, file_path: Path) -> bool:
        """检查是否为音频文件"""
        audio_extensions = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".wma"}
        return file_path.suffix.lower() in audio_extensions

    def _is_image_file(self, file_path: Path) -> bool:
        """检查是否为图片文件"""
        image_extensions = {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".tiff",
        }
        return file_path.suffix.lower() in image_extensions

    def _is_document_file(self, file_path: Path) -> bool:
        """检查是否为文档文件"""
        doc_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",
            ".odt",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        }
        return file_path.suffix.lower() in doc_extensions


# 全局服务实例
qiniu_storage_service = QiniuStorageService()
