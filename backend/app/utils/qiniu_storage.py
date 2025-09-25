"""
七牛云存储工具类

提供文件上传、下载、删除等基础操作功能
"""

import hashlib
import mimetypes
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

from qiniu import Auth, BucketManager, CdnManager, put_data, put_file
from qiniu.http import ResponseInfo

from app.core.config import settings
from app.core.logger import logger


class QiniuStorageError(Exception):
    """七牛云存储异常"""

    pass


class QiniuStorageClient:
    """七牛云存储客户端"""

    def __init__(self):
        """初始化七牛云客户端"""
        if not all(
            [
                settings.QINIU_ACCESS_KEY,
                settings.QINIU_SECRET_KEY,
                settings.QINIU_BUCKET_NAME,
                settings.QINIU_DOMAIN,
            ]
        ):
            logger.error("七牛云配置不完整，请检查环境变量")
            raise QiniuStorageError("七牛云配置不完整，请检查环境变量")

        self.auth = Auth(settings.QINIU_ACCESS_KEY, settings.QINIU_SECRET_KEY)
        self.bucket_manager = BucketManager(self.auth)
        self.cdn_manager = CdnManager(self.auth)
        self.bucket_name = settings.QINIU_BUCKET_NAME
        self.domain = settings.QINIU_DOMAIN.rstrip("/") if settings.QINIU_DOMAIN else ""
        self.use_https = settings.QINIU_USE_HTTPS
        self.cdn_domain = (settings.QINIU_CDN_DOMAIN or settings.QINIU_DOMAIN or "").rstrip("/")

    def _get_protocol(self) -> str:
        """获取协议"""
        return "https" if self.use_https else "http"

    def _generate_file_key(self, file_path: str, prefix: str = "") -> str:
        """
        生成文件在七牛云中的key

        Args:
            file_path: 文件路径
            prefix: 文件前缀

        Returns:
            str: 七牛云文件key
        """
        path = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d")
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        file_name = f"{file_hash}_{path.name}"

        if prefix:
            return f"{prefix}/{timestamp}/{file_name}"
        return f"{timestamp}/{file_name}"

    def _get_public_url(self, key: str) -> str:
        """
        公共 URL，不签名。适合公开 bucket 或已配置 CDN 的情况。
        """
        domain = self.cdn_domain or self.domain
        protocol = self._get_protocol()
        return f"{protocol}://{domain}/{key}"

    def _get_private_url(self, key: str, expires: int = 3600) -> str:
        """
        私有 URL，会生成签名。适合私有 bucket。
        """
        domain = self.domain or self.cdn_domain
        protocol = self._get_protocol()
        base_url = f"{protocol}://{domain}/{key}"
        return self.auth.private_download_url(base_url, expires=expires)

    def upload_file(
        self,
        file_path: Union[str, Path],
        key: Optional[str] = None,
        prefix: str = "",
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """
        上传文件到七牛云

        Args:
            file_path: 本地文件路径
            key: 七牛云文件key，如果不提供则自动生成
            prefix: 文件前缀
            overwrite: 是否覆盖同名文件

        Returns:
            Dict: 上传结果信息

        Raises:
            QiniuStorageError: 上传失败时抛出
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise QiniuStorageError(f"文件不存在: {file_path}")

        if not key:
            key = self._generate_file_key(str(file_path), prefix)

        # 生成上传token
        policy = {
            "scope": f"{self.bucket_name}:{key}",
            "deadline": int((datetime.now() + timedelta(hours=1)).timestamp()),
            "returnBody": '{"key":"$(key)","hash":"$(etag)","fsize":$(fsize),"bucket":"$(bucket)","name":"$(x:name)"}',
        }

        if not overwrite:
            policy["insertOnly"] = 1

        token = self.auth.upload_token(self.bucket_name, key, 3600, policy)

        # 上传文件
        ret, info = put_file(token, key, str(file_path))

        if info.status_code != 200:
            raise QiniuStorageError(f"上传失败: {info}")

        return {
            "key": ret.get("key"),
            "hash": ret.get("hash"),
            "fsize": ret.get("fsize"),
            "bucket": ret.get("bucket"),
            "url": self._get_public_url(key),
            "private_url": self._get_private_url(key),
        }

    def upload_data(
        self,
        data: bytes,
        key: str,
        content_type: Optional[str] = None,
        overwrite: bool = False,
    ) -> Dict[str, Any]:
        """
        上传字节数据到七牛云

        Args:
            data: 要上传的数据
            key: 七牛云文件key
            content_type: 文件类型
            overwrite: 是否覆盖同名文件

        Returns:
            Dict: 上传结果信息

        Raises:
            QiniuStorageError: 上传失败时抛出
        """
        # 生成上传token
        policy = {
            "scope": f"{self.bucket_name}:{key}",
            "deadline": int((datetime.now() + timedelta(hours=1)).timestamp()),
            "returnBody": '{"key":"$(key)","hash":"$(etag)","fsize":$(fsize),"bucket":"$(bucket)","name":"$(x:name)"}',
        }

        if not overwrite:
            policy["insertOnly"] = 1

        token = self.auth.upload_token(self.bucket_name, key, 3600, policy)

        # 上传数据
        ret, info = put_data(token, key, data, mime_type=content_type)

        if info.status_code != 200:
            raise QiniuStorageError(f"上传失败: {info}")

        return {
            "key": ret.get("key"),
            "hash": ret.get("hash"),
            "fsize": ret.get("fsize"),
            "bucket": ret.get("bucket"),
            "url": self._get_public_url(key),
            "private_url": self._get_private_url(key),
        }

    def delete_file(self, key: str) -> bool:
        """
        删除七牛云文件

        Args:
            key: 文件key

        Returns:
            bool: 删除是否成功
        """
        ret, info = self.bucket_manager.delete(self.bucket_name, key)
        return info.status_code == 200

    def delete_files(self, keys: List[str]) -> Dict[str, Any]:
        """
        批量删除文件

        Args:
            keys: 文件key列表

        Returns:
            Dict: 删除结果
        """
        from qiniu import build_batch_delete

        ops = build_batch_delete(self.bucket_name, keys)
        ret, info = self.bucket_manager.batch(ops)

        return {"success": info.status_code == 200, "result": ret, "info": info}

    def get_file_info(self, key: str) -> Optional[Dict[str, Any]]:
        """
        获取文件信息

        Args:
            key: 文件key

        Returns:
            Optional[Dict]: 文件信息，如果文件不存在返回None
        """
        ret, info = self.bucket_manager.stat(self.bucket_name, key)

        if info.status_code == 200:
            return ret
        return None

    def list_files(
        self, prefix: str = "", limit: int = 1000, marker: str = ""
    ) -> Dict[str, Any]:
        """
        列出文件

        Args:
            prefix: 文件前缀
            limit: 返回数量限制
            marker: 分页标记

        Returns:
            Dict: 文件列表信息
        """
        ret, eof, info = self.bucket_manager.list(
            self.bucket_name, prefix=prefix, limit=limit, marker=marker
        )

        if info.status_code != 200:
            raise QiniuStorageError(f"获取文件列表失败: {info}")

        return ret

    def copy_file(
        self, src_key: str, dest_key: str, src_bucket: Optional[str] = None
    ) -> bool:
        """
        复制文件

        Args:
            src_key: 源文件key
            dest_key: 目标文件key
            src_bucket: 源存储桶，默认使用当前存储桶

        Returns:
            bool: 复制是否成功
        """
        src_bucket = src_bucket or self.bucket_name
        ret, info = self.bucket_manager.copy(
            src_bucket, src_key, self.bucket_name, dest_key
        )
        return info.status_code == 200

    def move_file(
        self, src_key: str, dest_key: str, src_bucket: Optional[str] = None
    ) -> bool:
        """
        移动文件

        Args:
            src_key: 源文件key
            dest_key: 目标文件key
            src_bucket: 源存储桶，默认使用当前存储桶

        Returns:
            bool: 移动是否成功
        """
        src_bucket = src_bucket or self.bucket_name
        ret, info = self.bucket_manager.move(
            src_bucket, src_key, self.bucket_name, dest_key
        )
        return info.status_code == 200

    def refresh_cdn(self, urls: List[str]) -> Dict[str, Any]:
        """
        刷新CDN缓存

        Args:
            urls: 要刷新的URL列表

        Returns:
            Dict: 刷新结果
        """
        ret, info = self.cdn_manager.refresh_urls(urls)
        return {"success": info.status_code == 200, "result": ret, "info": info}

    def get_upload_token(
        self,
        key: Optional[str] = None,
        expires: int = 3600,
        policy: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        获取上传token

        Args:
            key: 文件key，如果不提供则允许上传到任意位置
            expires: 过期时间（秒）
            policy: 上传策略

        Returns:
            str: 上传token
        """
        if key:
            scope = f"{self.bucket_name}:{key}"
        else:
            scope = self.bucket_name

        return self.auth.upload_token(scope, key, expires, policy)

    def get_image_url_with_params(
        self, key: str, params: str = "", expires: int = 3600, private: bool = False
    ) -> str:
        """
        带图片处理参数的 URL。
        - private=False：返回普通 CDN 地址
        - private=True ：对带参数的完整 URL 签名
        """
        protocol = self._get_protocol()
        domain = self.cdn_domain or self.domain
        if not domain:
            raise QiniuStorageError("没有配置 QINIU_DOMAIN 或 QINIU_CDN_DOMAIN")

        if params:
            base = f"{protocol}://{domain}/{key}?{params}"
        else:
            base = f"{protocol}://{domain}/{key}"

        if private:
            return self.auth.private_download_url(base, expires=expires)
        return base


# 全局客户端实例
qiniu_client = QiniuStorageClient()
