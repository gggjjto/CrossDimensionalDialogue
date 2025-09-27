"""
任务队列服务
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.core.logger import get_logger
from app.core.rq import queue_manager
from app.models.task import AITask, TaskStatus, TaskType
from app.schemas.task import (
    STTTranscriptionTaskInput,
    TaskCreateRequest,
    TaskListRequest,
    TaskListResponse,
    TaskResponse,
    TaskStatsResponse,
    TaskStatusUpdate,
    TextMessageTaskInput,
    TTSGenerationTaskInput,
    VoiceMessageTaskInput,
)
from sqlmodel import Session, select

logger = get_logger("task_queue_service")


class TaskQueueService:
    """任务队列服务"""

    def __init__(self):
        self.queue_manager = queue_manager

    async def create_task(
        self, db: Session, user_id: uuid.UUID, request: TaskCreateRequest
    ) -> TaskResponse:
        """创建任务"""
        try:
            # 生成任务ID
            task_id = f"{request.task_type.value}_{uuid.uuid4().hex[:12]}"

            # 创建任务记录
            task = AITask(
                id=task_id,
                user_id=user_id,
                conversation_id=request.conversation_id,
                task_type=request.task_type,
                status=TaskStatus.PENDING,
                input_data=request.input_data,
                priority=request.priority,
                max_retries=request.max_retries,
                task_metadata=request.task_metadata,
                created_at=datetime.utcnow(),
            )

            # 根据任务类型设置处理步骤
            task.steps = self._get_task_steps(request.task_type)

            # 保存到数据库
            db.add(task)
            db.commit()
            db.refresh(task)

            # 入队任务
            if settings.TASK_QUEUE_ENABLED:
                queue_name = self._get_queue_name(request.task_type, request.priority)
                depends_on_job = None

                # 若提供会话ID，则将同一会话的任务串行化（依赖上一个未完成任务）
                if request.conversation_id:
                    try:
                        # 查找同一会话中最新的、尚未结束的任务（不包含当前任务）
                        prev_stmt = (
                            select(AITask)
                            .where(
                                AITask.conversation_id == request.conversation_id,
                                AITask.id != task_id,
                            )
                            .order_by(AITask.created_at.desc())
                        )
                        prev_tasks = db.exec(prev_stmt).all()
                        for prev in prev_tasks:
                            # 仅当存在RQ作业且状态不是【已完成/失败/已取消】时才作为依赖
                            if prev.rq_job_id and prev.status not in [
                                TaskStatus.COMPLETED,
                                TaskStatus.FAILED,
                                TaskStatus.CANCELLED,
                            ]:
                                depends_on_job = self.queue_manager.get_job(
                                    prev.rq_job_id
                                )
                                break
                    except Exception:
                        depends_on_job = None

                rq_job = self.queue_manager.enqueue_task(
                    queue_name=queue_name,
                    func=self._get_task_function(request.task_type),
                    task_id=task_id,
                    timeout=settings.TASK_DEFAULT_TIMEOUT,
                    retry=settings.TASK_DEFAULT_RETRY,
                    result_ttl=settings.TASK_RESULT_TTL,
                    failure_ttl=settings.TASK_FAILURE_TTL,
                    depends_on=depends_on_job,
                )

                # 更新RQ任务ID
                task.rq_job_id = rq_job.id
                db.add(task)
                db.commit()
                db.refresh(task)

            logger.info(f"任务已创建: {task_id}, 类型: {request.task_type}")
            return TaskResponse.model_validate(task)

        except Exception as e:
            logger.error(f"创建任务失败: {str(e)}")
            db.rollback()
            raise

    async def get_task(
        self, db: Session, task_id: str, user_id: uuid.UUID
    ) -> Optional[TaskResponse]:
        """获取任务"""
        try:
            statement = select(AITask).where(
                AITask.id == task_id, AITask.user_id == user_id
            )
            task = db.exec(statement).first()

            if not task:
                return None

            return TaskResponse.from_orm(task)

        except Exception as e:
            logger.error(f"获取任务失败: {task_id}, 错误: {str(e)}")
            return None

    async def update_task_status(
        self, db: Session, task_id: str, update: TaskStatusUpdate
    ) -> bool:
        """更新任务状态"""
        try:
            statement = select(AITask).where(AITask.id == task_id)
            task = db.exec(statement).first()

            if not task:
                return False

            # 更新任务状态
            task.status = update.status
            if update.progress is not None:
                task.progress = update.progress
            if update.error is not None:
                task.error = update.error
            if update.result is not None:
                task.result = update.result

            # 更新时间戳
            if update.status == TaskStatus.PROCESSING and not task.started_at:
                task.started_at = datetime.utcnow()
            elif update.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ]:
                task.completed_at = datetime.utcnow()

            # 更新步骤状态
            if update.step_name and update.step_result is not None:
                for step in task.steps:
                    if step.name == update.step_name:
                        step.status = TaskStatus.COMPLETED
                        step.completed_at = datetime.utcnow()
                        step.result = update.step_result
                        break

            db.add(task)
            db.commit()
            db.refresh(task)

            logger.info(f"任务状态已更新: {task_id}, 状态: {update.status}")
            return True

        except Exception as e:
            logger.error(f"更新任务状态失败: {task_id}, 错误: {str(e)}")
            db.rollback()
            return False

    async def get_user_tasks(
        self, db: Session, user_id: uuid.UUID, request: TaskListRequest
    ) -> TaskListResponse:
        """获取用户任务列表"""
        try:
            # 构建查询条件
            statement = select(AITask).where(AITask.user_id == user_id)

            if request.task_type:
                statement = statement.where(AITask.task_type == request.task_type)
            if request.status:
                statement = statement.where(AITask.status == request.status)
            if request.conversation_id:
                statement = statement.where(
                    AITask.conversation_id == request.conversation_id
                )

            # 排序
            if request.order_by == "created_at":
                if request.order == "desc":
                    statement = statement.order_by(AITask.created_at.desc())
                else:
                    statement = statement.order_by(AITask.created_at.asc())
            elif request.order_by == "priority":
                if request.order == "desc":
                    statement = statement.order_by(AITask.priority.desc())
                else:
                    statement = statement.order_by(AITask.priority.asc())

            # 分页
            total_statement = select(AITask).where(AITask.user_id == user_id)
            if request.task_type:
                total_statement = total_statement.where(
                    AITask.task_type == request.task_type
                )
            if request.status:
                total_statement = total_statement.where(AITask.status == request.status)
            if request.conversation_id:
                total_statement = total_statement.where(
                    AITask.conversation_id == request.conversation_id
                )

            total = len(db.exec(total_statement).all())

            statement = statement.offset(request.skip).limit(request.limit)
            tasks = db.exec(statement).all()

            return TaskListResponse(
                tasks=[TaskResponse.from_orm(task) for task in tasks],
                total=total,
                skip=request.skip,
                limit=request.limit,
            )

        except Exception as e:
            logger.error(f"获取任务列表失败: {str(e)}")
            raise

    async def cancel_task(
        self,
        db: Session,
        task_id: str,
        user_id: uuid.UUID,
        reason: Optional[str] = None,
    ) -> bool:
        """取消任务"""
        try:
            statement = select(AITask).where(
                AITask.id == task_id, AITask.user_id == user_id
            )
            task = db.exec(statement).first()

            if not task:
                return False

            # 检查任务状态
            if task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ]:
                return False

            # 取消RQ任务
            if task.rq_job_id:
                self.queue_manager.cancel_job(task.rq_job_id)

            # 更新任务状态
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            if reason:
                task.error = f"用户取消: {reason}"

            db.add(task)
            db.commit()
            db.refresh(task)

            logger.info(f"任务已取消: {task_id}")
            return True

        except Exception as e:
            logger.error(f"取消任务失败: {task_id}, 错误: {str(e)}")
            db.rollback()
            return False

    async def get_task_stats(
        self, db: Session, user_id: uuid.UUID
    ) -> TaskStatsResponse:
        """获取任务统计"""
        try:
            statement = select(AITask).where(AITask.user_id == user_id)
            tasks = db.exec(statement).all()

            total_tasks = len(tasks)
            pending_tasks = len([t for t in tasks if t.status == TaskStatus.PENDING])
            processing_tasks = len(
                [t for t in tasks if t.status == TaskStatus.PROCESSING]
            )
            completed_tasks = len(
                [t for t in tasks if t.status == TaskStatus.COMPLETED]
            )
            failed_tasks = len([t for t in tasks if t.status == TaskStatus.FAILED])
            cancelled_tasks = len(
                [t for t in tasks if t.status == TaskStatus.CANCELLED]
            )

            success_rate = 0.0
            if total_tasks > 0:
                success_rate = completed_tasks / total_tasks

            # 计算平均处理时间
            completed_tasks_with_time = [
                t
                for t in tasks
                if t.status == TaskStatus.COMPLETED and t.started_at and t.completed_at
            ]
            average_processing_time = None
            if completed_tasks_with_time:
                total_time = sum(
                    (t.completed_at - t.started_at).total_seconds()
                    for t in completed_tasks_with_time
                )
                average_processing_time = total_time / len(completed_tasks_with_time)

            return TaskStatsResponse(
                total_tasks=total_tasks,
                pending_tasks=pending_tasks,
                processing_tasks=processing_tasks,
                completed_tasks=completed_tasks,
                failed_tasks=failed_tasks,
                cancelled_tasks=cancelled_tasks,
                success_rate=success_rate,
                average_processing_time=average_processing_time,
            )

        except Exception as e:
            logger.error(f"获取任务统计失败: {str(e)}")
            raise

    def _get_task_steps(self, task_type: TaskType) -> List[Dict[str, Any]]:
        """根据任务类型获取处理步骤"""
        steps_map = {
            TaskType.VOICE_MESSAGE: [
                {"name": "stt", "status": TaskStatus.PENDING.value},
                {"name": "llm", "status": TaskStatus.PENDING.value},
                {"name": "tts", "status": TaskStatus.PENDING.value},
            ],
            TaskType.TEXT_MESSAGE: [
                {"name": "llm", "status": TaskStatus.PENDING.value},
                {"name": "tts", "status": TaskStatus.PENDING.value},
            ],
            TaskType.TTS_GENERATION: [
                {"name": "tts", "status": TaskStatus.PENDING.value},
            ],
            TaskType.STT_TRANSCRIPTION: [
                {"name": "stt", "status": TaskStatus.PENDING.value},
            ],
            TaskType.IMAGE_GENERATION: [
                {"name": "image_generation", "status": TaskStatus.PENDING.value},
            ],
            TaskType.CHARACTER_GENERATION: [
                {"name": "character_generation", "status": TaskStatus.PENDING.value},
            ],
        }
        return steps_map.get(task_type, [])

    def _get_queue_name(self, task_type: TaskType, priority: int) -> str:
        """根据任务类型和优先级获取队列名称"""
        if priority > 5:
            return "priority_queue"

        queue_map = {
            TaskType.VOICE_MESSAGE: "voice_queue",
            TaskType.TEXT_MESSAGE: "text_queue",
            TaskType.TTS_GENERATION: "voice_queue",
            TaskType.STT_TRANSCRIPTION: "voice_queue",
            TaskType.IMAGE_GENERATION: "image_queue",
            TaskType.CHARACTER_GENERATION: "text_queue",
        }
        return queue_map.get(task_type, "text_queue")

    def _get_task_function(self, task_type: TaskType) -> str:
        """获取任务处理函数路径"""
        function_map = {
            TaskType.VOICE_MESSAGE: "app.workers.ai_task_worker.process_voice_message_task",
            TaskType.TEXT_MESSAGE: "app.workers.ai_task_worker.process_text_message_task",
            TaskType.TTS_GENERATION: "app.workers.ai_task_worker.process_tts_generation_task",
            TaskType.STT_TRANSCRIPTION: "app.workers.ai_task_worker.process_stt_transcription_task",
            TaskType.IMAGE_GENERATION: "app.workers.ai_task_worker.process_image_generation_task",
            TaskType.CHARACTER_GENERATION: "app.workers.ai_task_worker.process_character_generation_task",
        }
        return function_map.get(
            task_type, "app.workers.ai_task_worker.process_text_message_task"
        )


# 全局任务队列服务实例
task_queue_service = TaskQueueService()
