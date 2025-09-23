import uuid
from typing import Any, Dict, List, Optional, Tuple, Union
from sqlmodel import Session, select, func, and_, or_

from app.models.voice import (
    VoiceMessage,
    VoiceMessageCreate,
    VoiceConfig,
    VoiceConfigCreate,
    VoiceConfigUpdate,
    AudioProcessingTask,
    AudioProcessingTaskCreate,
    VoiceMessageStats,
    AudioProcessingStatus,
    VoiceLanguage,
    AudioQuality,
)


class VoiceCRUD:
    """语音消息CRUD操作"""

    def create(self, db: Session, *, obj_in: VoiceMessageCreate) -> VoiceMessage:
        """创建语音消息"""
        db_obj = VoiceMessage.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[VoiceMessage]:
        """根据ID获取语音消息"""
        return db.get(VoiceMessage, id)

    def get_by_user(
        self, db: Session, *, id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[VoiceMessage]:
        """根据ID和用户ID获取语音消息"""
        statement = select(VoiceMessage).where(
            and_(VoiceMessage.id == id, VoiceMessage.sender_id == user_id)
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[VoiceMessage], int]:
        """获取语音消息列表"""
        statement = select(VoiceMessage)

        # 应用过滤器
        if filters:
            for key, value in filters.items():
                if hasattr(VoiceMessage, key) and value is not None:
                    statement = statement.where(getattr(VoiceMessage, key) == value)

        # 应用用户过滤
        if user_id:
            statement = statement.where(VoiceMessage.sender_id == user_id)

        # 获取总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        # 获取数据
        statement = (
            statement.offset(skip).limit(limit).order_by(VoiceMessage.created_at.desc())
        )
        results = db.exec(statement).all()

        return results, total

    def update(
        self,
        db: Session,
        *,
        db_obj: VoiceMessage,
        obj_in: Union[Dict[str, Any], VoiceMessageCreate]
    ) -> VoiceMessage:
        """更新语音消息"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> VoiceMessage:
        """删除语音消息"""
        obj = db.get(VoiceMessage, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_voice_stats(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None
    ) -> VoiceMessageStats:
        """获取语音消息统计"""
        # 构建查询条件
        conditions = [VoiceMessage.sender_id == user_id]
        if conversation_id:
            conditions.append(VoiceMessage.conversation_id == conversation_id)

        # 基础查询
        base_query = select(VoiceMessage).where(and_(*conditions))

        # 总消息数
        total_messages = db.exec(
            select(func.count()).select_from(base_query.subquery())
        ).one()

        # 总时长
        total_duration = (
            db.exec(
                select(func.sum(VoiceMessage.duration)).where(and_(*conditions))
            ).one()
            or 0.0
        )

        # 平均时长
        average_duration = (
            total_duration / total_messages if total_messages > 0 else 0.0
        )

        # 总文件大小
        total_file_size = (
            db.exec(
                select(func.sum(VoiceMessage.file_size)).where(and_(*conditions))
            ).one()
            or 0
        )

        # 语言分布
        language_dist = {}
        language_results = db.exec(
            select(VoiceMessage.language, func.count())
            .where(and_(*conditions))
            .group_by(VoiceMessage.language)
        ).all()
        for lang, count in language_results:
            language_dist[lang] = count

        # 质量分布
        quality_dist = {}
        quality_results = db.exec(
            select(VoiceMessage.audio_quality, func.count())
            .where(and_(*conditions))
            .group_by(VoiceMessage.audio_quality)
        ).all()
        for quality, count in quality_results:
            quality_dist[quality] = count

        # 处理状态分布
        status_dist = {}
        status_results = db.exec(
            select(VoiceMessage.processing_status, func.count())
            .where(and_(*conditions))
            .group_by(VoiceMessage.processing_status)
        ).all()
        for status, count in status_results:
            status_dist[status] = count

        return VoiceMessageStats(
            total_messages=total_messages,
            total_duration=total_duration,
            average_duration=average_duration,
            total_file_size=total_file_size,
            language_distribution=language_dist,
            quality_distribution=quality_dist,
            processing_status_distribution=status_dist,
        )


class VoiceConfigCRUD:
    """语音配置CRUD操作"""

    def create_voice_config(
        self, db: Session, *, obj_in: VoiceConfigCreate
    ) -> VoiceConfig:
        """创建语音配置"""
        db_obj = VoiceConfig.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_voice_config(self, db: Session, *, id: uuid.UUID) -> Optional[VoiceConfig]:
        """根据ID获取语音配置"""
        return db.get(VoiceConfig, id)

    def get_voice_configs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[VoiceConfig], int]:
        """获取语音配置列表"""
        statement = select(VoiceConfig)

        # 应用过滤器
        if filters:
            for key, value in filters.items():
                if hasattr(VoiceConfig, key) and value is not None:
                    statement = statement.where(getattr(VoiceConfig, key) == value)

        # 获取总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        # 获取数据
        statement = (
            statement.offset(skip).limit(limit).order_by(VoiceConfig.created_at.desc())
        )
        results = db.exec(statement).all()

        return results, total

    def update_voice_config(
        self, db: Session, *, db_obj: VoiceConfig, obj_in: VoiceConfigUpdate
    ) -> VoiceConfig:
        """更新语音配置"""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_voice_config(self, db: Session, *, id: uuid.UUID) -> VoiceConfig:
        """删除语音配置"""
        obj = db.get(VoiceConfig, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


class AudioProcessingTaskCRUD:
    """音频处理任务CRUD操作"""

    def create_task(
        self, db: Session, *, obj_in: AudioProcessingTaskCreate
    ) -> AudioProcessingTask:
        """创建音频处理任务"""
        db_obj = AudioProcessingTask.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_processing_task(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[AudioProcessingTask]:
        """根据ID获取处理任务"""
        return db.get(AudioProcessingTask, id)

    def get_processing_tasks(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[AudioProcessingTask], int]:
        """获取处理任务列表"""
        statement = select(AudioProcessingTask)

        # 应用过滤器
        if filters:
            for key, value in filters.items():
                if hasattr(AudioProcessingTask, key) and value is not None:
                    statement = statement.where(
                        getattr(AudioProcessingTask, key) == value
                    )

        # 应用用户过滤
        if user_id:
            statement = statement.where(AudioProcessingTask.user_id == user_id)

        # 获取总数
        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        # 获取数据
        statement = (
            statement.offset(skip)
            .limit(limit)
            .order_by(AudioProcessingTask.created_at.desc())
        )
        results = db.exec(statement).all()

        return results, total

    def update_task(
        self,
        db: Session,
        *,
        db_obj: AudioProcessingTask,
        obj_in: Union[Dict[str, Any], AudioProcessingTaskCreate]
    ) -> AudioProcessingTask:
        """更新处理任务"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_task(self, db: Session, *, id: uuid.UUID) -> AudioProcessingTask:
        """删除处理任务"""
        obj = db.get(AudioProcessingTask, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_tasks_by_status(
        self, db: Session, *, status: AudioProcessingStatus
    ) -> List[AudioProcessingTask]:
        """根据状态获取处理任务"""
        statement = select(AudioProcessingTask).where(
            AudioProcessingTask.status == status
        )
        return db.exec(statement).all()

    def get_failed_tasks(self, db: Session) -> List[AudioProcessingTask]:
        """获取失败的处理任务"""
        return self.get_tasks_by_status(db, status=AudioProcessingStatus.FAILED)

    def get_pending_tasks(self, db: Session) -> List[AudioProcessingTask]:
        """获取待处理的任务"""
        return self.get_tasks_by_status(db, status=AudioProcessingStatus.PENDING)


# 创建CRUD实例
voice_crud = VoiceCRUD()
voice_config_crud = VoiceConfigCRUD()
audio_processing_task_crud = AudioProcessingTaskCRUD()


# 为了向后兼容，创建统一的voice_crud
class UnifiedVoiceCRUD:
    """统一的语音CRUD操作"""

    def __init__(self):
        self.voice = voice_crud
        self.config = voice_config_crud
        self.task = audio_processing_task_crud

    # 语音消息操作
    def create(self, db: Session, *, obj_in: VoiceMessageCreate) -> VoiceMessage:
        return self.voice.create(db, obj_in=obj_in)

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[VoiceMessage]:
        return self.voice.get(db, id=id)

    def get_by_user(
        self, db: Session, *, id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[VoiceMessage]:
        return self.voice.get_by_user(db, id=id, user_id=user_id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[VoiceMessage], int]:
        return self.voice.get_multi(
            db, skip=skip, limit=limit, filters=filters, user_id=user_id
        )

    def update(
        self,
        db: Session,
        *,
        db_obj: VoiceMessage,
        obj_in: Union[Dict[str, Any], VoiceMessageCreate]
    ) -> VoiceMessage:
        return self.voice.update(db, db_obj=db_obj, obj_in=obj_in)

    def delete(self, db: Session, *, id: uuid.UUID) -> VoiceMessage:
        return self.voice.delete(db, id=id)

    def get_voice_stats(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None
    ) -> VoiceMessageStats:
        return self.voice.get_voice_stats(
            db, user_id=user_id, conversation_id=conversation_id
        )

    # 语音配置操作
    def create_voice_config(
        self, db: Session, *, obj_in: VoiceConfigCreate
    ) -> VoiceConfig:
        return self.config.create_voice_config(db, obj_in=obj_in)

    def get_voice_config(self, db: Session, *, id: uuid.UUID) -> Optional[VoiceConfig]:
        return self.config.get_voice_config(db, id=id)

    def get_voice_configs(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[VoiceConfig], int]:
        return self.config.get_voice_configs(
            db, skip=skip, limit=limit, filters=filters
        )

    def update_voice_config(
        self, db: Session, *, db_obj: VoiceConfig, obj_in: VoiceConfigUpdate
    ) -> VoiceConfig:
        return self.config.update_voice_config(db, db_obj=db_obj, obj_in=obj_in)

    def delete_voice_config(self, db: Session, *, id: uuid.UUID) -> VoiceConfig:
        return self.config.delete_voice_config(db, id=id)

    # 处理任务操作
    def create_processing_task(
        self, db: Session, *, obj_in: AudioProcessingTaskCreate
    ) -> AudioProcessingTask:
        return self.task.create_task(db, obj_in=obj_in)

    def get_processing_task(
        self, db: Session, *, id: uuid.UUID
    ) -> Optional[AudioProcessingTask]:
        return self.task.get_processing_task(db, id=id)

    def get_processing_tasks(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        user_id: Optional[uuid.UUID] = None
    ) -> Tuple[List[AudioProcessingTask], int]:
        return self.task.get_processing_tasks(
            db, skip=skip, limit=limit, filters=filters, user_id=user_id
        )

    def update_processing_task(
        self,
        db: Session,
        *,
        db_obj: AudioProcessingTask,
        obj_in: Union[Dict[str, Any], AudioProcessingTaskCreate]
    ) -> AudioProcessingTask:
        return self.task.update_task(db, db_obj=db_obj, obj_in=obj_in)

    def delete_processing_task(
        self, db: Session, *, id: uuid.UUID
    ) -> AudioProcessingTask:
        return self.task.delete_task(db, id=id)


# 导出统一的CRUD实例
voice_crud = UnifiedVoiceCRUD()
