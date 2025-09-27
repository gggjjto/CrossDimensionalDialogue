"""
Redis连接配置
"""

from typing import Optional

import redis
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger("redis")


class RedisClient:
    """Redis客户端单例"""

    _instance: Optional["RedisClient"] = None
    _redis_client: Optional[redis.Redis] = None

    def __new__(cls) -> "RedisClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._redis_client is None:
            self._connect()

    def _connect(self):
        """建立Redis连接"""
        try:
            # 解析Redis URL
            redis_url = getattr(settings, "REDIS_URL", "redis://localhost:6379/0")

            # 创建连接池 - RQ需要二进制数据，不使用decode_responses
            self._redis_client = redis.from_url(
                redis_url,
                decode_responses=False,  # RQ需要二进制数据
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=20,
            )

            # 测试连接
            self._redis_client.ping()
            logger.info("Redis连接成功")

        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise

    @property
    def client(self) -> redis.Redis:
        """获取Redis客户端"""
        if self._redis_client is None:
            self._connect()
        return self._redis_client

    async def health_check(self) -> bool:
        """健康检查"""
        try:
            self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis健康检查失败: {str(e)}")
            return False

    def close(self):
        """关闭连接"""
        if self._redis_client:
            self._redis_client.close()
            self._redis_client = None


# 全局Redis客户端实例
redis_client = RedisClient()
