import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlmodel import Session

from app.models.websocket import (
    SystemNotification,
    WebSocketMessageType,
    RealtimeMessage,
    RealtimeMessageCreate,
    UserOnlineStatus,
    TypingStatus,
    MessageBroadcast,
)
from app.models.conversation import Conversation, Message, SenderType, ContentType
from app.crud.conversation import conversation, message as message_crud
from app.services.websocket_manager import websocket_manager
from app.services.websocket_handlers import websocket_event_handler
from app.core.db import get_db


class RealtimeMessageService:
    """实时消息服务"""

    def __init__(self):
        self.websocket_manager = websocket_manager
        self.event_handler = websocket_event_handler

    async def send_message_to_conversation(
        self,
        conversation_id: uuid.UUID,
        message_data: Dict[str, Any],
        sender_id: uuid.UUID,
        sender_type: SenderType = SenderType.USER,
    ) -> bool:
        """发送消息到会话"""
        try:
            # 创建消息并保存到数据库
            db = next(get_db())
            try:
                message_create = message_crud.MessageCreate(
                    content=message_data.get("content", ""),
                    content_type=ContentType(message_data.get("content_type", "text")),
                    sender_type=sender_type,
                    sender_id=sender_id,
                    metadata=message_data.get("metadata"),
                )

                db_message = message_crud.create(
                    db, obj_in=message_create, conversation_id=conversation_id
                )

                # 更新会话消息计数和最后消息时间
                db_conversation = conversation.get_by_user_and_id(
                    db, id=conversation_id, user_id=sender_id
                )
                if db_conversation:
                    db_conversation.message_count += 1
                    db_conversation.last_message_at = datetime.utcnow()
                    db_conversation.updated_at = datetime.utcnow()
                    db.add(db_conversation)
                    db.commit()

                # 广播消息到WebSocket连接
                await self._broadcast_message_to_conversation(
                    conversation_id, db_message
                )

                # 触发消息创建事件
                await self.event_handler.handle_event(
                    "message_created",
                    {
                        "conversation_id": conversation_id,
                        "message": {
                            "id": str(db_message.id),
                            "conversation_id": str(conversation_id),
                            "content": db_message.content,
                            "content_type": db_message.content_type,
                            "sender_type": db_message.sender_type,
                            "sender_id": str(db_message.sender_id),
                            "metadata": db_message.message_metadata,
                            "status": "sent",
                            "created_at": db_message.created_at.isoformat(),
                        },
                    },
                )

                return True

            finally:
                db.close()

        except Exception as e:
            print(f"发送消息到会话失败: {e}")
            return False

    async def update_message_in_conversation(
        self,
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
        updates: Dict[str, Any],
        user_id: uuid.UUID,
    ) -> bool:
        """更新会话中的消息"""
        try:
            db = next(get_db())
            try:
                # 获取消息
                db_message = message_crud.get_by_conversation_and_id(
                    db, id=message_id, conversation_id=conversation_id
                )

                if not db_message:
                    return False

                # 检查权限
                if (
                    db_message.sender_type == SenderType.USER
                    and db_message.sender_id != user_id
                ):
                    return False

                # 更新消息
                message_update = message_crud.MessageUpdate(**updates)
                updated_message = message_crud.update(
                    db, db_obj=db_message, obj_in=message_update
                )

                # 广播更新到WebSocket连接
                await self._broadcast_message_update_to_conversation(
                    conversation_id, message_id, updates
                )

                # 触发消息更新事件
                await self.event_handler.handle_event(
                    "message_updated",
                    {
                        "conversation_id": conversation_id,
                        "message_id": str(message_id),
                        "updates": updates,
                    },
                )

                return True

            finally:
                db.close()

        except Exception as e:
            print(f"更新消息失败: {e}")
            return False

    async def delete_message_from_conversation(
        self, conversation_id: uuid.UUID, message_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """从会话中删除消息"""
        try:
            db = next(get_db())
            try:
                # 获取消息
                db_message = message_crud.get_by_conversation_and_id(
                    db, id=message_id, conversation_id=conversation_id
                )

                if not db_message:
                    return False

                # 检查权限
                if (
                    db_message.sender_type == SenderType.USER
                    and db_message.sender_id != user_id
                ):
                    return False

                # 删除消息
                success = message_crud.delete(db, id=message_id)

                if success:
                    # 更新会话消息计数
                    db_conversation = conversation.get_by_user_and_id(
                        db, id=conversation_id, user_id=user_id
                    )
                    if db_conversation:
                        db_conversation.message_count = max(
                            0, db_conversation.message_count - 1
                        )
                        db_conversation.updated_at = datetime.utcnow()
                        db.add(db_conversation)
                        db.commit()

                    # 广播删除到WebSocket连接
                    await self._broadcast_message_delete_to_conversation(
                        conversation_id, message_id
                    )

                    # 触发消息删除事件
                    await self.event_handler.handle_event(
                        "message_deleted",
                        {
                            "conversation_id": conversation_id,
                            "message_id": str(message_id),
                        },
                    )

                return success

            finally:
                db.close()

        except Exception as e:
            print(f"删除消息失败: {e}")
            return False

    async def send_typing_status(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID, is_typing: bool
    ) -> bool:
        """发送输入状态"""
        try:
            # 获取用户的所有连接
            user_connections = await self.websocket_manager.get_user_connections(
                user_id
            )

            if not user_connections:
                return False

            # 为所有连接发送输入状态
            success_count = 0
            for connection_id in user_connections:
                if await self.websocket_manager.send_typing_status(
                    connection_id, conversation_id, is_typing
                ):
                    success_count += 1

            return success_count > 0

        except Exception as e:
            print(f"发送输入状态失败: {e}")
            return False

    async def notify_conversation_created(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """通知会话创建"""
        await self.event_handler.handle_event(
            "conversation_created",
            {"conversation_id": conversation_id, "user_id": user_id},
        )

    async def notify_conversation_updated(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID, updates: Dict[str, Any]
    ) -> None:
        """通知会话更新"""
        await self.event_handler.handle_event(
            "conversation_updated",
            {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "updates": updates,
            },
        )

    async def notify_conversation_deleted(
        self, conversation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """通知会话删除"""
        await self.event_handler.handle_event(
            "conversation_deleted",
            {"conversation_id": conversation_id, "user_id": user_id},
        )

    async def send_system_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        target_users: List[uuid.UUID] = None,
        target_conversations: List[uuid.UUID] = None,
        data: Dict[str, Any] = None,
    ) -> int:
        """发送系统通知"""
        notification = SystemNotification(
            notification_type=notification_type,
            title=title,
            message=message,
            target_users=target_users or [],
            target_conversations=target_conversations or [],
            data=data,
        )

        return await self.websocket_manager.broadcast_system_notification(notification)

    async def _broadcast_message_to_conversation(
        self, conversation_id: uuid.UUID, message: Message
    ) -> None:
        """广播消息到会话"""
        await self.websocket_manager._broadcast_to_conversation(
            conversation_id,
            {
                "type": WebSocketMessageType.MESSAGE_RECEIVE,
                "data": {
                    "message": {
                        "id": str(message.id),
                        "conversation_id": str(conversation_id),
                        "content": message.content,
                        "content_type": message.content_type,
                        "sender_type": message.sender_type,
                        "sender_id": str(message.sender_id),
                        "metadata": message.message_metadata,
                        "status": "sent",
                        "created_at": message.created_at.isoformat(),
                    },
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    async def _broadcast_message_update_to_conversation(
        self, conversation_id: uuid.UUID, message_id: uuid.UUID, updates: Dict[str, Any]
    ) -> None:
        """广播消息更新到会话"""
        await self.websocket_manager._broadcast_to_conversation(
            conversation_id,
            {
                "type": WebSocketMessageType.MESSAGE_UPDATE,
                "data": {
                    "message_id": str(message_id),
                    "updates": updates,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )

    async def _broadcast_message_delete_to_conversation(
        self, conversation_id: uuid.UUID, message_id: uuid.UUID
    ) -> None:
        """广播消息删除到会话"""
        await self.websocket_manager._broadcast_to_conversation(
            conversation_id,
            {
                "type": WebSocketMessageType.MESSAGE_DELETE,
                "data": {
                    "message_id": str(message_id),
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        )


class RealtimePresenceService:
    """实时在线状态服务"""

    def __init__(self):
        self.websocket_manager = websocket_manager

    async def get_user_online_status(
        self, user_id: uuid.UUID
    ) -> Optional[UserOnlineStatus]:
        """获取用户在线状态"""
        return self.websocket_manager.user_online_status.get(user_id)

    async def get_online_users(self) -> List[uuid.UUID]:
        """获取在线用户列表"""
        return await self.websocket_manager.get_online_users()

    async def get_conversation_participants(
        self, conversation_id: uuid.UUID
    ) -> List[uuid.UUID]:
        """获取会话参与者"""
        return await self.websocket_manager.get_conversation_participants(
            conversation_id
        )

    async def is_user_online(self, user_id: uuid.UUID) -> bool:
        """检查用户是否在线"""
        return user_id in self.websocket_manager.user_online_status

    async def get_user_connections(self, user_id: uuid.UUID) -> List[str]:
        """获取用户的所有连接"""
        return await self.websocket_manager.get_user_connections(user_id)


class RealtimeNotificationService:
    """实时通知服务"""

    def __init__(self):
        self.websocket_manager = websocket_manager
        self.realtime_service = RealtimeMessageService()

    async def send_message_notification(
        self,
        conversation_id: uuid.UUID,
        message_id: uuid.UUID,
        sender_id: uuid.UUID,
        content: str,
        exclude_user: uuid.UUID = None,
    ) -> None:
        """发送消息通知"""
        # 获取会话参与者
        participants = await self.websocket_manager.get_conversation_participants(
            conversation_id
        )

        # 发送通知给所有参与者（除了发送者）
        for user_id in participants:
            if user_id != sender_id and (not exclude_user or user_id != exclude_user):
                await self.websocket_manager.send_to_user(
                    user_id,
                    {
                        "type": "message_notification",
                        "data": {
                            "conversation_id": str(conversation_id),
                            "message_id": str(message_id),
                            "sender_id": str(sender_id),
                            "content": (
                                content[:100] + "..." if len(content) > 100 else content
                            ),
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    },
                )

    async def send_conversation_notification(
        self,
        conversation_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Dict[str, Any] = None,
    ) -> None:
        """发送会话通知"""
        await self.realtime_service.send_system_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            target_conversations=[conversation_id],
            data=data,
        )

    async def send_user_notification(
        self,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: str,
        data: Dict[str, Any] = None,
    ) -> None:
        """发送用户通知"""
        await self.realtime_service.send_system_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            target_users=[user_id],
            data=data,
        )


# 全局服务实例
realtime_message_service = RealtimeMessageService()
realtime_presence_service = RealtimePresenceService()
realtime_notification_service = RealtimeNotificationService()
