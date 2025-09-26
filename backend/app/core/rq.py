"""
RQ队列配置
"""

from typing import Dict, List, Optional

from app.core.logger import get_logger
from app.core.redis import redis_client
from rq import Queue, Worker
from rq.job import Job

logger = get_logger("rq")


class QueueManager:
    """队列管理器"""

    def __init__(self):
        self._queues: Dict[str, Queue] = {}
        self._connection = redis_client.client

    def get_queue(self, queue_name: str) -> Queue:
        """获取队列"""
        if queue_name not in self._queues:
            self._queues[queue_name] = Queue(
                name=queue_name,
                connection=self._connection,
                default_timeout=300,  # 5分钟超时
            )
        return self._queues[queue_name]

    def get_voice_queue(self) -> Queue:
        """获取语音处理队列"""
        return self.get_queue("voice_queue")

    def get_text_queue(self) -> Queue:
        """获取文本处理队列"""
        return self.get_queue("text_queue")

    def get_image_queue(self) -> Queue:
        """获取图像处理队列"""
        return self.get_queue("image_queue")

    def get_priority_queue(self) -> Queue:
        """获取高优先级队列"""
        return self.get_queue("priority_queue")

    def enqueue_task(self, queue_name: str, func, *args, **kwargs) -> Job:
        """入队任务"""
        queue = self.get_queue(queue_name)

        # 提取RQ特定的参数
        timeout = kwargs.pop("timeout", 300)
        retry_count = kwargs.pop("retry", 3)
        result_ttl = kwargs.pop("result_ttl", 3600)
        failure_ttl = kwargs.pop("failure_ttl", 86400)

        # 移除其他不支持的参数
        kwargs.pop("job_timeout", None)

        # 入队任务
        try:
            # 使用 enqueue_call 明确区分函数参数与RQ作业选项
            job = queue.enqueue_call(
                func=func,
                args=list(args) if args else None,
                kwargs=kwargs or None,
                timeout=timeout,
                result_ttl=result_ttl,
                failure_ttl=failure_ttl,
            )
        except Exception as e:
            logger.error(f"入队任务失败: {str(e)}")
            return None

        logger.info(f"任务已入队: {job.id}, 队列: {queue_name}")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """获取任务"""
        try:
            return Job.fetch(job_id, connection=self._connection)
        except Exception as e:
            logger.error(f"获取任务失败: {job_id}, 错误: {str(e)}")
            return None

    def get_queue_stats(self, queue_name: str) -> Dict:
        """获取队列统计信息"""
        queue = self.get_queue(queue_name)
        return {
            "name": queue_name,
            "count": len(queue),
            "failed_count": queue.failed_job_registry.count,
            "started_count": queue.started_job_registry.count,
            "finished_count": queue.finished_job_registry.count,
            "scheduled_count": queue.scheduled_job_registry.count,
        }

    def get_all_queue_stats(self) -> Dict[str, Dict]:
        """获取所有队列统计信息"""
        stats = {}
        for queue_name in self._queues.keys():
            stats[queue_name] = self.get_queue_stats(queue_name)
        return stats

    def clear_queue(self, queue_name: str):
        """清空队列"""
        queue = self.get_queue(queue_name)
        queue.empty()
        logger.info(f"队列已清空: {queue_name}")

    def cancel_job(self, job_id: str) -> bool:
        """取消任务"""
        job = self.get_job(job_id)
        if job and job.get_status() in ["queued", "started"]:
            job.cancel()
            logger.info(f"任务已取消: {job_id}")
            return True
        return False


# 全局队列管理器实例
queue_manager = QueueManager()
