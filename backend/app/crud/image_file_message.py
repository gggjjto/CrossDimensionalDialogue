"""
图片和文件消息CRUD操作
"""

import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlmodel import Session, select, and_, or_, func, desc, asc

from app.models.image_file_message import (
    ImageMessage,
    ImageMessageCreate,
    ImageMessageUpdate,
    FileMessage,
    FileMessageCreate,
    FileMessageUpdate,
    FileProcessingTask,
    FileProcessingTaskCreate,
    FileProcessingTaskUpdate,
    ProcessingStatus,
    SecurityScanStatus,
    TaskType,
)


class ImageMessageCRUD:
    """图片消息CRUD操作类"""

    def create(self, db: Session, *, obj_in: ImageMessageCreate) -> ImageMessage:
        """创建图片消息"""
        db_obj = ImageMessage(
            **obj_in.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[ImageMessage]:
        """根据ID获取图片消息"""
        return db.get(ImageMessage, id)

    def get_by_message_id(
        self, db: Session, *, message_id: uuid.UUID
    ) -> Optional[ImageMessage]:
        """根据消息ID获取图片消息"""
        statement = select(ImageMessage).where(ImageMessage.message_id == message_id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        conversation_id: Optional[uuid.UUID] = None,
        format: Optional[str] = None,
        status: Optional[ProcessingStatus] = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> Tuple[List[ImageMessage], int]:
        """获取图片消息列表"""
        query = select(ImageMessage)

        # 添加过滤条件
        if conversation_id:
            query = query.join(ImageMessage.message).where(
                ImageMessage.message.has(conversation_id=conversation_id)
            )

        if format:
            query = query.where(ImageMessage.format == format)

        if status:
            query = query.where(ImageMessage.processing_status == status)

        # 添加排序
        if order_by == "created_at":
            order_column = ImageMessage.created_at
        elif order_by == "file_size":
            order_column = ImageMessage.file_size
        elif order_by == "updated_at":
            order_column = ImageMessage.updated_at
        else:
            order_column = ImageMessage.created_at

        if order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).one()

        # 分页
        query = query.offset(skip).limit(limit)
        results = db.exec(query).all()

        return results, total

    def update(
        self, db: Session, *, db_obj: ImageMessage, obj_in: ImageMessageUpdate
    ) -> ImageMessage:
        """更新图片消息"""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> Optional[ImageMessage]:
        """删除图片消息"""
        db_obj = db.get(ImageMessage, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def get_by_conversation(
        self, db: Session, *, conversation_id: uuid.UUID
    ) -> List[ImageMessage]:
        """获取会话的所有图片消息"""
        statement = (
            select(ImageMessage)
            .join(ImageMessage.message)
            .where(ImageMessage.message.has(conversation_id=conversation_id))
            .order_by(desc(ImageMessage.created_at))
        )
        return db.exec(statement).all()


class FileMessageCRUD:
    """文件消息CRUD操作类"""

    def create(self, db: Session, *, obj_in: FileMessageCreate) -> FileMessage:
        """创建文件消息"""
        db_obj = FileMessage(
            **obj_in.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[FileMessage]:
        """根据ID获取文件消息"""
        return db.get(FileMessage, id)

    def get_by_message_id(
        self, db: Session, *, message_id: uuid.UUID
    ) -> Optional[FileMessage]:
        """根据消息ID获取文件消息"""
        statement = select(FileMessage).where(FileMessage.message_id == message_id)
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        conversation_id: Optional[uuid.UUID] = None,
        file_type: Optional[str] = None,
        status: Optional[ProcessingStatus] = None,
        security_status: Optional[SecurityScanStatus] = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> Tuple[List[FileMessage], int]:
        """获取文件消息列表"""
        query = select(FileMessage)

        # 添加过滤条件
        if conversation_id:
            query = query.join(FileMessage.message).where(
                FileMessage.message.has(conversation_id=conversation_id)
            )

        if file_type:
            query = query.where(FileMessage.file_type == file_type)

        if status:
            query = query.where(FileMessage.processing_status == status)

        if security_status:
            query = query.where(FileMessage.security_scan_status == security_status)

        # 添加排序
        if order_by == "created_at":
            order_column = FileMessage.created_at
        elif order_by == "file_size":
            order_column = FileMessage.file_size
        elif order_by == "download_count":
            order_column = FileMessage.download_count
        elif order_by == "updated_at":
            order_column = FileMessage.updated_at
        else:
            order_column = FileMessage.created_at

        if order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).one()

        # 分页
        query = query.offset(skip).limit(limit)
        results = db.exec(query).all()

        return results, total

    def update(
        self, db: Session, *, db_obj: FileMessage, obj_in: FileMessageUpdate
    ) -> FileMessage:
        """更新文件消息"""
        update_data = obj_in.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> Optional[FileMessage]:
        """删除文件消息"""
        db_obj = db.get(FileMessage, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def increment_download_count(
        self, db: Session, *, db_obj: FileMessage
    ) -> FileMessage:
        """增加下载次数"""
        db_obj.download_count += 1
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation(
        self, db: Session, *, conversation_id: uuid.UUID
    ) -> List[FileMessage]:
        """获取会话的所有文件消息"""
        statement = (
            select(FileMessage)
            .join(FileMessage.message)
            .where(FileMessage.message.has(conversation_id=conversation_id))
            .order_by(desc(FileMessage.created_at))
        )
        return db.exec(statement).all()


class FileProcessingTaskCRUD:
    """文件处理任务CRUD操作类"""

    def create(
        self, db: Session, *, obj_in: FileProcessingTaskCreate
    ) -> FileProcessingTask:
        """创建文件处理任务"""
        db_obj = FileProcessingTask(
            **obj_in.dict(),
            created_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[FileProcessingTask]:
        """根据ID获取文件处理任务"""
        return db.get(FileProcessingTask, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        file_message_id: Optional[uuid.UUID] = None,
        image_message_id: Optional[uuid.UUID] = None,
        task_type: Optional[TaskType] = None,
        status: Optional[ProcessingStatus] = None,
        order_by: str = "created_at",
        order: str = "desc",
    ) -> Tuple[List[FileProcessingTask], int]:
        """获取文件处理任务列表"""
        query = select(FileProcessingTask)

        # 添加过滤条件
        if file_message_id:
            query = query.where(FileProcessingTask.file_message_id == file_message_id)

        if image_message_id:
            query = query.where(FileProcessingTask.image_message_id == image_message_id)

        if task_type:
            query = query.where(FileProcessingTask.task_type == task_type)

        if status:
            query = query.where(FileProcessingTask.status == status)

        # 添加排序
        if order_by == "created_at":
            order_column = FileProcessingTask.created_at
        elif order_by == "started_at":
            order_column = FileProcessingTask.started_at
        elif order_by == "completed_at":
            order_column = FileProcessingTask.completed_at
        else:
            order_column = FileProcessingTask.created_at

        if order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = db.exec(count_query).one()

        # 分页
        query = query.offset(skip).limit(limit)
        results = db.exec(query).all()

        return results, total

    def update(
        self,
        db: Session,
        *,
        db_obj: FileProcessingTask,
        obj_in: FileProcessingTaskUpdate,
    ) -> FileProcessingTask:
        """更新文件处理任务"""
        update_data = obj_in.dict(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> Optional[FileProcessingTask]:
        """删除文件处理任务"""
        db_obj = db.get(FileProcessingTask, id)
        if db_obj:
            db.delete(db_obj)
            db.commit()
        return db_obj

    def get_pending_tasks(
        self, db: Session, *, limit: int = 10
    ) -> List[FileProcessingTask]:
        """获取待处理的任务"""
        statement = (
            select(FileProcessingTask)
            .where(FileProcessingTask.status == ProcessingStatus.PENDING)
            .order_by(asc(FileProcessingTask.created_at))
            .limit(limit)
        )
        return db.exec(statement).all()

    def get_processing_tasks(
        self, db: Session, *, limit: int = 10
    ) -> List[FileProcessingTask]:
        """获取正在处理的任务"""
        statement = (
            select(FileProcessingTask)
            .where(FileProcessingTask.status == ProcessingStatus.PROCESSING)
            .order_by(asc(FileProcessingTask.started_at))
            .limit(limit)
        )
        return db.exec(statement).all()


# 创建CRUD实例
image_message = ImageMessageCRUD()
file_message = FileMessageCRUD()
file_processing_task = FileProcessingTaskCRUD()
