"""
Worker启动脚本（兼容 Windows/Linux）
"""

import platform
import sys

from app.core.logger import get_logger
from app.core.redis import redis_client
from rq import Queue, SimpleWorker, Worker

logger = get_logger("worker_script")


def start_worker(queue_names=None):
    """启动Worker"""
    if queue_names is None:
        queue_names = ["voice_queue", "text_queue", "image_queue", "priority_queue"]

    logger.info(f"启动Worker，监听队列: {queue_names}")

    try:
        # 创建队列列表
        queue_list = [
            Queue(name, connection=redis_client.client) for name in queue_names
        ]

        # 检测操作系统
        system = platform.system().lower()
        logger.info(f"检测到操作系统: {system}")

        # 根据系统选择 Worker 类型
        if system == "windows":  # Windows/Win11
            logger.info("使用 SimpleWorker 运行（无 fork）")
            worker = SimpleWorker(queue_list, connection=redis_client.client)
        else:  # Linux / macOS / WSL
            logger.info("使用 Worker 运行（启用 fork）")
            worker = Worker(queue_list, connection=redis_client.client)

        worker.work(with_scheduler=True)

    except KeyboardInterrupt:
        logger.info("Worker 停止")
    except Exception as e:
        logger.error(f"Worker 启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # 从命令行参数获取队列名称
    queue_names = sys.argv[1:] if len(sys.argv) > 1 else None
    start_worker(queue_names)
