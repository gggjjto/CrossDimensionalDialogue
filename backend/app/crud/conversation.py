import uuid
from datetime import datetime
from typing import List, Optional, Tuple

from sqlmodel import Session, select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from app.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationUpdate,
    ConversationSearchRequest,
    ConversationStatus,
    Message,
    MessageCreate,
    MessageUpdate,
    MessageSearchRequest,
    SenderType,
    ContentType,
    MessageStatus,
    ConversationContext,
    ConversationContextCreate,
    ConversationTag,
    ConversationTagCreate,
    UserConversationLimit,
    UserConversationLimitCreate,
)


class ConversationCRUD:
    """会话CRUD操作类"""

    def create(
        self, db: Session, *, obj_in: ConversationCreate, user_id: uuid.UUID
    ) -> Conversation:
        """创建会话"""
        db_obj = Conversation(
            **obj_in.dict(),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[Conversation]:
        """根据ID获取会话"""
        return db.get(Conversation, id)

    def get_by_user_and_id(
        self, db: Session, *, id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Conversation]:
        """根据ID和用户ID获取会话"""
        statement = select(Conversation).where(
            and_(
                Conversation.id == id,
                Conversation.user_id == user_id,
                Conversation.deleted_at.is_(None),
            )
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
        status: Optional[ConversationStatus] = None,
        character_id: Optional[uuid.UUID] = None,
        order_by: str = "last_message_at",
        order: str = "desc",
    ) -> Tuple[List[Conversation], int]:
        """获取用户会话列表"""
        statement = select(Conversation).where(
            and_(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        )

        # 应用过滤条件
        if status:
            statement = statement.where(Conversation.status == status)
        if character_id:
            statement = statement.where(Conversation.character_id == character_id)

        # 应用排序
        if order_by == "created_at":
            if order == "desc":
                statement = statement.order_by(desc(Conversation.created_at))
            else:
                statement = statement.order_by(asc(Conversation.created_at))
        elif order_by == "last_message_at":
            if order == "desc":
                statement = statement.order_by(desc(Conversation.last_message_at))
            else:
                statement = statement.order_by(asc(Conversation.last_message_at))
        else:
            statement = statement.order_by(desc(Conversation.updated_at))

        # 获取总数
        count_statement = select(func.count(Conversation.id)).where(
            and_(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        )
        if status:
            count_statement = count_statement.where(Conversation.status == status)
        if character_id:
            count_statement = count_statement.where(
                Conversation.character_id == character_id
            )

        total = db.exec(count_statement).one()

        # 应用分页
        statement = statement.offset(skip).limit(limit)

        # 预加载关联数据
        statement = statement.options(
            selectinload(Conversation.character), selectinload(Conversation.user)
        )

        conversations = db.exec(statement).all()
        return conversations, total

    def search(
        self,
        db: Session,
        *,
        user_id: uuid.UUID,
        search_params: ConversationSearchRequest,
    ) -> Tuple[List[Conversation], int]:
        """搜索会话"""
        statement = select(Conversation).where(
            and_(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        )

        # 应用搜索条件
        if search_params.query:
            statement = statement.where(
                or_(
                    Conversation.title.ilike(f"%{search_params.query}%"),
                    Conversation.description.ilike(f"%{search_params.query}%"),
                )
            )

        if search_params.status:
            statement = statement.where(Conversation.status == search_params.status)

        if search_params.character_id:
            statement = statement.where(
                Conversation.character_id == search_params.character_id
            )

        # 应用排序
        if search_params.order_by == "created_at":
            if search_params.order == "desc":
                statement = statement.order_by(desc(Conversation.created_at))
            else:
                statement = statement.order_by(asc(Conversation.created_at))
        elif search_params.order_by == "last_message_at":
            if search_params.order == "desc":
                statement = statement.order_by(desc(Conversation.last_message_at))
            else:
                statement = statement.order_by(asc(Conversation.last_message_at))
        else:
            statement = statement.order_by(desc(Conversation.updated_at))

        # 获取总数
        count_statement = select(func.count(Conversation.id)).where(
            and_(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        )

        if search_params.query:
            count_statement = count_statement.where(
                or_(
                    Conversation.title.ilike(f"%{search_params.query}%"),
                    Conversation.description.ilike(f"%{search_params.query}%"),
                )
            )

        if search_params.status:
            count_statement = count_statement.where(
                Conversation.status == search_params.status
            )

        if search_params.character_id:
            count_statement = count_statement.where(
                Conversation.character_id == search_params.character_id
            )

        total = db.exec(count_statement).one()

        # 应用分页
        statement = statement.offset(search_params.skip).limit(search_params.limit)

        # 预加载关联数据
        statement = statement.options(
            selectinload(Conversation.character), selectinload(Conversation.user)
        )

        conversations = db.exec(statement).all()
        return conversations, total

    def update(
        self, db: Session, *, db_obj: Conversation, obj_in: ConversationUpdate
    ) -> Conversation:
        """更新会话"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(
        self, db: Session, *, id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[Conversation]:
        """软删除会话"""
        db_obj = self.get_by_user_and_id(db, id=id, user_id=user_id)
        if not db_obj:
            return None

        db_obj.deleted_at = datetime.utcnow()
        db_obj.status = ConversationStatus.ENDED
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def hard_delete(self, db: Session, *, id: uuid.UUID) -> bool:
        """硬删除会话"""
        db_obj = self.get(db, id=id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True

    def get_user_conversation_count(self, db: Session, *, user_id: uuid.UUID) -> int:
        """获取用户会话数量"""
        statement = select(func.count(Conversation.id)).where(
            and_(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
        )
        return db.exec(statement).one()


class MessageCRUD:
    """消息CRUD操作类"""

    def create(
        self, db: Session, *, obj_in: MessageCreate, conversation_id: uuid.UUID
    ) -> Message:
        """创建消息"""
        db_obj = Message(
            **obj_in.dict(),
            conversation_id=conversation_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[Message]:
        """根据ID获取消息"""
        return db.get(Message, id)

    def get_by_conversation_and_id(
        self, db: Session, *, id: uuid.UUID, conversation_id: uuid.UUID
    ) -> Optional[Message]:
        """根据ID和会话ID获取消息"""
        statement = select(Message).where(
            and_(Message.id == id, Message.conversation_id == conversation_id)
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        conversation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
        sender_type: Optional[SenderType] = None,
        content_type: Optional[ContentType] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> Tuple[List[Message], int]:
        """获取会话消息列表"""
        statement = select(Message).where(Message.conversation_id == conversation_id)

        # 应用过滤条件
        if sender_type:
            statement = statement.where(Message.sender_type == sender_type)
        if content_type:
            statement = statement.where(Message.content_type == content_type)
        if since:
            statement = statement.where(Message.created_at >= since)
        if until:
            statement = statement.where(Message.created_at <= until)

        # 按时间排序
        statement = statement.order_by(desc(Message.created_at))

        # 获取总数
        count_statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )

        if sender_type:
            count_statement = count_statement.where(Message.sender_type == sender_type)
        if content_type:
            count_statement = count_statement.where(
                Message.content_type == content_type
            )
        if since:
            count_statement = count_statement.where(Message.created_at >= since)
        if until:
            count_statement = count_statement.where(Message.created_at <= until)

        total = db.exec(count_statement).one()

        # 应用分页
        statement = statement.offset(skip).limit(limit)

        messages = db.exec(statement).all()
        return messages, total

    def search(
        self,
        db: Session,
        *,
        conversation_id: uuid.UUID,
        search_params: MessageSearchRequest,
    ) -> Tuple[List[Message], int]:
        """搜索消息"""
        statement = select(Message).where(Message.conversation_id == conversation_id)

        # 应用搜索条件
        if search_params.query:
            statement = statement.where(
                Message.content.ilike(f"%{search_params.query}%")
            )

        if search_params.sender_type:
            statement = statement.where(
                Message.sender_type == search_params.sender_type
            )

        if search_params.content_type:
            statement = statement.where(
                Message.content_type == search_params.content_type
            )

        if search_params.since:
            statement = statement.where(Message.created_at >= search_params.since)

        if search_params.until:
            statement = statement.where(Message.created_at <= search_params.until)

        # 按时间排序
        statement = statement.order_by(desc(Message.created_at))

        # 获取总数
        count_statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )

        if search_params.query:
            count_statement = count_statement.where(
                Message.content.ilike(f"%{search_params.query}%")
            )

        if search_params.sender_type:
            count_statement = count_statement.where(
                Message.sender_type == search_params.sender_type
            )

        if search_params.content_type:
            count_statement = count_statement.where(
                Message.content_type == search_params.content_type
            )

        if search_params.since:
            count_statement = count_statement.where(
                Message.created_at >= search_params.since
            )

        if search_params.until:
            count_statement = count_statement.where(
                Message.created_at <= search_params.until
            )

        total = db.exec(count_statement).one()

        # 应用分页
        statement = statement.offset(search_params.skip).limit(search_params.limit)

        messages = db.exec(statement).all()
        return messages, total

    def update(self, db: Session, *, db_obj: Message, obj_in: MessageUpdate) -> Message:
        """更新消息"""
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> bool:
        """删除消息"""
        db_obj = self.get(db, id=id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True

    def get_conversation_message_count(
        self, db: Session, *, conversation_id: uuid.UUID
    ) -> int:
        """获取会话消息数量"""
        statement = select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id
        )
        return db.exec(statement).one()

    def get_latest_message(
        self, db: Session, *, conversation_id: uuid.UUID
    ) -> Optional[Message]:
        """获取会话最新消息"""
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        return db.exec(statement).first()


class ConversationContextCRUD:
    """会话上下文CRUD操作类"""

    def create(
        self, db: Session, *, obj_in: ConversationContextCreate
    ) -> ConversationContext:
        """创建会话上下文"""
        db_obj = ConversationContext(
            **obj_in.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation(
        self,
        db: Session,
        *,
        conversation_id: uuid.UUID,
        context_type: Optional[str] = None,
    ) -> List[ConversationContext]:
        """获取会话上下文"""
        statement = select(ConversationContext).where(
            ConversationContext.conversation_id == conversation_id
        )

        if context_type:
            statement = statement.where(
                ConversationContext.context_type == context_type
            )

        statement = statement.order_by(desc(ConversationContext.importance_score))

        return db.exec(statement).all()

    def delete_by_conversation(self, db: Session, *, conversation_id: uuid.UUID) -> int:
        """删除会话的所有上下文"""
        statement = select(ConversationContext).where(
            ConversationContext.conversation_id == conversation_id
        )
        contexts = db.exec(statement).all()

        for context in contexts:
            db.delete(context)

        db.commit()
        return len(contexts)


class ConversationTagCRUD:
    """会话标签CRUD操作类"""

    def create(self, db: Session, *, obj_in: ConversationTagCreate) -> ConversationTag:
        """创建会话标签"""
        db_obj = ConversationTag(**obj_in.dict(), created_at=datetime.utcnow())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_conversation(
        self, db: Session, *, conversation_id: uuid.UUID
    ) -> List[ConversationTag]:
        """获取会话标签"""
        statement = (
            select(ConversationTag)
            .where(ConversationTag.conversation_id == conversation_id)
            .order_by(ConversationTag.created_at)
        )
        return db.exec(statement).all()

    def delete_by_conversation(self, db: Session, *, conversation_id: uuid.UUID) -> int:
        """删除会话的所有标签"""
        statement = select(ConversationTag).where(
            ConversationTag.conversation_id == conversation_id
        )
        tags = db.exec(statement).all()

        for tag in tags:
            db.delete(tag)

        db.commit()
        return len(tags)


class UserConversationLimitCRUD:
    """用户会话限制CRUD操作类"""

    def create(
        self, db: Session, *, obj_in: UserConversationLimitCreate
    ) -> UserConversationLimit:
        """创建用户会话限制"""
        db_obj = UserConversationLimit(
            **obj_in.dict(), created_at=datetime.utcnow(), updated_at=datetime.utcnow()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_user_and_type(
        self, db: Session, *, user_id: uuid.UUID, limit_type: str
    ) -> Optional[UserConversationLimit]:
        """获取用户特定类型的限制"""
        statement = select(UserConversationLimit).where(
            and_(
                UserConversationLimit.user_id == user_id,
                UserConversationLimit.limit_type == limit_type,
            )
        )
        return db.exec(statement).first()

    def update_current_value(
        self, db: Session, *, db_obj: UserConversationLimit, increment: int = 1
    ) -> UserConversationLimit:
        """更新当前值"""
        db_obj.current_value += increment
        db_obj.updated_at = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def reset_if_needed(
        self, db: Session, *, db_obj: UserConversationLimit
    ) -> UserConversationLimit:
        """如果需要则重置限制"""
        if datetime.utcnow() >= db_obj.reset_at:
            db_obj.current_value = 0
            if db_obj.limit_type == "daily_messages":
                db_obj.reset_at = datetime.utcnow().replace(
                    hour=0, minute=0, second=0, microsecond=0
                )
                db_obj.reset_at = db_obj.reset_at.replace(day=db_obj.reset_at.day + 1)
            elif db_obj.limit_type == "hourly_messages":
                db_obj.reset_at = datetime.utcnow().replace(
                    minute=0, second=0, microsecond=0
                )
                db_obj.reset_at = db_obj.reset_at.replace(hour=db_obj.reset_at.hour + 1)

            db_obj.updated_at = datetime.utcnow()
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

        return db_obj


# 创建CRUD实例
conversation = ConversationCRUD()
message = MessageCRUD()
conversation_context = ConversationContextCRUD()
conversation_tag = ConversationTagCRUD()
user_conversation_limit = UserConversationLimitCRUD()
