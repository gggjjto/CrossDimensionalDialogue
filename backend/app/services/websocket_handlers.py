import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import WebSocket, WebSocketDisconnect
from sqlmodel import Session

from app.models.websocket import (
    WebSocketMessageType,
    WebSocketMessageStatus,
    RealtimeMessage,
    RealtimeMessageCreate,
    SystemNotification,
    WebSocketError,
    Heartbeat,
)
from app.models.conversation import SenderType, ContentType, MessageCreate
from app.crud.conversation import conversation, message
from app.services.websocket_manager import websocket_manager
from app.core.db import get_db


class WebSocketMessageHandler:
    """WebSocket消息处理器"""

    def __init__(self):
        self.handlers = {
            WebSocketMessageType.PING: self._handle_ping,
            WebSocketMessageType.PONG: self._handle_pong,
            WebSocketMessageType.JOIN_CONVERSATION: self._handle_join_conversation,
            WebSocketMessageType.LEAVE_CONVERSATION: self._handle_leave_conversation,
            WebSocketMessageType.MESSAGE_SEND: self._handle_message_send,
            WebSocketMessageType.MESSAGE_TYPING: self._handle_typing,
            WebSocketMessageType.MESSAGE_TYPING_STOP: self._handle_typing_stop,
            WebSocketMessageType.HEARTBEAT: self._handle_heartbeat,
        }

    async def handle_message(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        message_data: Dict[str, Any],
    ) -> None:
        """处理WebSocket消息"""
        try:
            message_type = message_data.get("type")
            data = message_data.get("data", {})

            if message_type in self.handlers:
                await self.handlers[message_type](
                    websocket, connection_id, user_id, data
                )
            else:
                await self._send_error(websocket, f"未知的消息类型: {message_type}")

        except Exception as e:
            print(f"处理消息错误: {e}")
            await self._send_error(websocket, f"处理消息时发生错误: {str(e)}")

    async def _handle_ping(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理ping消息"""
        await websocket_manager.send_to_connection(
            connection_id,
            {
                "type": WebSocketMessageType.PONG,
                "data": {"timestamp": datetime.utcnow().isoformat()},
            },
        )

    async def _handle_pong(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理pong消息"""
        # 更新连接的最后活动时间
        connection_info = await websocket_manager.get_connection_info(connection_id)
        if connection_info:
            connection_info.last_activity = datetime.utcnow()

    async def _handle_join_conversation(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理加入会话消息"""
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            await self._send_error(websocket, "缺少会话ID")
            return

        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await self._send_error(websocket, "无效的会话ID格式")
            return

        success = await websocket_manager.join_conversation(
            connection_id, conversation_uuid
        )
        if success:
            await websocket_manager.send_to_connection(
                connection_id,
                {
                    "type": WebSocketMessageType.JOIN_CONVERSATION,
                    "data": {
                        "conversation_id": conversation_id,
                        "status": "success",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )
        else:
            await self._send_error(websocket, "加入会话失败，可能没有权限或会话不存在")

    async def _handle_leave_conversation(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理离开会话消息"""
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            await self._send_error(websocket, "缺少会话ID")
            return

        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await self._send_error(websocket, "无效的会话ID格式")
            return

        success = await websocket_manager.leave_conversation(
            connection_id, conversation_uuid
        )
        if success:
            await websocket_manager.send_to_connection(
                connection_id,
                {
                    "type": WebSocketMessageType.LEAVE_CONVERSATION,
                    "data": {
                        "conversation_id": conversation_id,
                        "status": "success",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )
        else:
            await self._send_error(websocket, "离开会话失败")

    async def _handle_message_send(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理发送消息"""
        conversation_id = data.get("conversation_id")
        content = data.get("content")
        content_type = data.get("content_type", "text")

        if not conversation_id or not content:
            await self._send_error(websocket, "缺少必要参数")
            return

        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await self._send_error(websocket, "无效的会话ID格式")
            return

        # 检查是否在会话房间中
        connection_info = await websocket_manager.get_connection_info(connection_id)
        if (
            not connection_info
            or conversation_uuid not in connection_info.active_conversations
        ):
            await self._send_error(websocket, "未加入该会话")
            return

        # 创建消息并保存到数据库
        try:
            db = next(get_db())
            try:
                # 创建消息
                message_create = MessageCreate(
                    content=content,
                    content_type=ContentType(content_type),
                    sender_type=SenderType.USER,
                    sender_id=user_id,
                    metadata=data.get("metadata"),
                )

                db_message = message.create(
                    db, obj_in=message_create, conversation_id=conversation_uuid
                )

                # 更新会话消息计数和最后消息时间
                db_conversation = conversation.get_by_user_and_id(
                    db, id=conversation_uuid, user_id=user_id
                )
                if db_conversation:
                    db_conversation.message_count += 1
                    db_conversation.last_message_at = datetime.utcnow()
                    db_conversation.updated_at = datetime.utcnow()
                    db.add(db_conversation)
                    db.commit()

                # 广播消息到会话房间
                await websocket_manager._broadcast_to_conversation(
                    conversation_uuid,
                    {
                        "type": WebSocketMessageType.MESSAGE_RECEIVE,
                        "data": {
                            "message": {
                                "id": str(db_message.id),
                                "conversation_id": str(conversation_uuid),
                                "content": db_message.content,
                                "content_type": db_message.content_type,
                                "sender_type": db_message.sender_type,
                                "sender_id": str(db_message.sender_id),
                                "metadata": db_message.message_metadata,
                                "status": "sent",
                                "created_at": db_message.created_at.isoformat(),
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    },
                )

                # 发送确认消息
                await websocket_manager.send_to_connection(
                    connection_id,
                    {
                        "type": "message_sent",
                        "data": {
                            "message_id": str(db_message.id),
                            "conversation_id": conversation_id,
                            "status": "success",
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    },
                )

            finally:
                db.close()

        except Exception as e:
            print(f"保存消息失败: {e}")
            await self._send_error(websocket, "保存消息失败")

    async def _handle_typing(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理输入状态开始"""
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            await self._send_error(websocket, "缺少会话ID")
            return

        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await self._send_error(websocket, "无效的会话ID格式")
            return

        await websocket_manager.send_typing_status(
            connection_id, conversation_uuid, True
        )

    async def _handle_typing_stop(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理输入状态结束"""
        conversation_id = data.get("conversation_id")
        if not conversation_id:
            await self._send_error(websocket, "缺少会话ID")
            return

        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await self._send_error(websocket, "无效的会话ID格式")
            return

        await websocket_manager.send_typing_status(
            connection_id, conversation_uuid, False
        )

    async def _handle_heartbeat(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: uuid.UUID,
        data: Dict[str, Any],
    ) -> None:
        """处理心跳消息"""
        heartbeat = Heartbeat(
            connection_id=connection_id,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            latency=data.get("latency"),
        )

        # 更新连接的最后活动时间
        connection_info = await websocket_manager.get_connection_info(connection_id)
        if connection_info:
            connection_info.last_activity = datetime.utcnow()

        # 发送心跳响应
        await websocket_manager.send_to_connection(
            connection_id,
            {
                "type": "heartbeat_response",
                "data": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "latency": heartbeat.latency,
                },
            },
        )

    async def _send_error(self, websocket: WebSocket, error_message: str) -> None:
        """发送错误消息"""
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": WebSocketMessageType.ERROR,
                        "data": {
                            "error_code": "MESSAGE_ERROR",
                            "error_message": error_message,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    }
                )
            )
        except Exception as e:
            print(f"发送错误消息失败: {e}")


class WebSocketEventHandler:
    """WebSocket事件处理器"""

    def __init__(self):
        self.event_handlers = {
            "conversation_created": self._handle_conversation_created,
            "conversation_updated": self._handle_conversation_updated,
            "conversation_deleted": self._handle_conversation_deleted,
            "message_created": self._handle_message_created,
            "message_updated": self._handle_message_updated,
            "message_deleted": self._handle_message_deleted,
            "user_joined": self._handle_user_joined,
            "user_left": self._handle_user_left,
        }

    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """处理事件"""
        if event_type in self.event_handlers:
            await self.event_handlers[event_type](event_data)

    async def _handle_conversation_created(self, event_data: Dict[str, Any]) -> None:
        """处理会话创建事件"""
        user_id = event_data.get("user_id")
        conversation_id = event_data.get("conversation_id")

        if user_id and conversation_id:
            # 通知用户会话创建成功
            await websocket_manager.send_to_user(
                user_id,
                {
                    "type": "conversation_created",
                    "data": {
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_conversation_updated(self, event_data: Dict[str, Any]) -> None:
        """处理会话更新事件"""
        user_id = event_data.get("user_id")
        conversation_id = event_data.get("conversation_id")
        updates = event_data.get("updates", {})

        if user_id and conversation_id:
            # 通知用户会话更新
            await websocket_manager.send_to_user(
                user_id,
                {
                    "type": "conversation_updated",
                    "data": {
                        "conversation_id": conversation_id,
                        "updates": updates,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

            # 通知会话房间内的其他用户
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": "conversation_updated",
                    "data": {
                        "conversation_id": conversation_id,
                        "updates": updates,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_conversation_deleted(self, event_data: Dict[str, Any]) -> None:
        """处理会话删除事件"""
        user_id = event_data.get("user_id")
        conversation_id = event_data.get("conversation_id")

        if user_id and conversation_id:
            # 通知用户会话删除
            await websocket_manager.send_to_user(
                user_id,
                {
                    "type": "conversation_deleted",
                    "data": {
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

            # 通知会话房间内的其他用户
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": "conversation_deleted",
                    "data": {
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_message_created(self, event_data: Dict[str, Any]) -> None:
        """处理消息创建事件"""
        conversation_id = event_data.get("conversation_id")
        message_data = event_data.get("message")

        if conversation_id and message_data:
            # 广播消息到会话房间
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": WebSocketMessageType.MESSAGE_RECEIVE,
                    "data": {
                        "message": message_data,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_message_updated(self, event_data: Dict[str, Any]) -> None:
        """处理消息更新事件"""
        conversation_id = event_data.get("conversation_id")
        message_id = event_data.get("message_id")
        updates = event_data.get("updates", {})

        if conversation_id and message_id:
            # 广播消息更新到会话房间
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": WebSocketMessageType.MESSAGE_UPDATE,
                    "data": {
                        "message_id": message_id,
                        "updates": updates,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_message_deleted(self, event_data: Dict[str, Any]) -> None:
        """处理消息删除事件"""
        conversation_id = event_data.get("conversation_id")
        message_id = event_data.get("message_id")

        if conversation_id and message_id:
            # 广播消息删除到会话房间
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": WebSocketMessageType.MESSAGE_DELETE,
                    "data": {
                        "message_id": message_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_user_joined(self, event_data: Dict[str, Any]) -> None:
        """处理用户加入事件"""
        conversation_id = event_data.get("conversation_id")
        user_id = event_data.get("user_id")

        if conversation_id and user_id:
            # 广播用户加入消息到会话房间
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": WebSocketMessageType.USER_ONLINE,
                    "data": {
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

    async def _handle_user_left(self, event_data: Dict[str, Any]) -> None:
        """处理用户离开事件"""
        conversation_id = event_data.get("conversation_id")
        user_id = event_data.get("user_id")

        if conversation_id and user_id:
            # 广播用户离开消息到会话房间
            await websocket_manager._broadcast_to_conversation(
                conversation_id,
                {
                    "type": WebSocketMessageType.USER_OFFLINE,
                    "data": {
                        "user_id": user_id,
                        "conversation_id": conversation_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )


# 全局处理器实例
websocket_message_handler = WebSocketMessageHandler()
websocket_event_handler = WebSocketEventHandler()
