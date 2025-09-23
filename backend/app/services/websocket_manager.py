import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from collections import defaultdict

from fastapi import WebSocket, WebSocketDisconnect

from app.models.websocket import (
    WebSocketConnectionInfo,
    WebSocketConnectionStatus,
    WebSocketMessage,
    WebSocketMessageType,
    RealtimeMessage,
    UserOnlineStatus,
    TypingStatus,
    SystemNotification,
)


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 活跃连接: connection_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}

        # 连接信息: connection_id -> WebSocketConnectionInfo
        self.connection_info: Dict[str, WebSocketConnectionInfo] = {}

        # 用户连接映射: user_id -> Set[connection_id]
        self.user_connections: Dict[uuid.UUID, Set[str]] = defaultdict(set)

        # 会话连接映射: conversation_id -> Set[connection_id]
        self.conversation_connections: Dict[uuid.UUID, Set[str]] = defaultdict(set)

        # 用户在线状态: user_id -> UserOnlineStatus
        self.user_online_status: Dict[uuid.UUID, UserOnlineStatus] = {}

        # 输入状态: conversation_id -> Dict[user_id, TypingStatus]
        self.typing_status: Dict[uuid.UUID, Dict[uuid.UUID, TypingStatus]] = (
            defaultdict(dict)
        )

        # 连接超时时间（秒）
        self.connection_timeout = 300  # 5分钟

        # 心跳间隔（秒）
        self.heartbeat_interval = 30  # 30秒

        # 清理任务将在需要时启动
        self._cleanup_task = None

    async def connect(
        self,
        websocket: WebSocket,
        user_id: uuid.UUID,
        conversation_id: Optional[uuid.UUID] = None,
    ) -> str:
        """建立WebSocket连接"""
        try:
            await websocket.accept()

            # 生成连接ID
            connection_id = str(uuid.uuid4())

            # 获取客户端信息
            client_info = websocket.client
            ip_address = client_info.host if client_info else None

            # 创建连接信息
            connection_info = WebSocketConnectionInfo(
                connection_id=connection_id,
                user_id=user_id,
                conversation_id=conversation_id,
                status=WebSocketConnectionStatus.CONNECTED,
                ip_address=ip_address,
                user_agent=None,  # 可以从headers获取
                connected_at=datetime.utcnow(),
                last_ping=None,
                last_pong=None,
            )

            # 存储连接
            self.active_connections[connection_id] = websocket
            self.connection_info[connection_id] = connection_info

            # 更新用户连接映射
            self.user_connections[user_id].add(connection_id)

            # 更新会话连接映射
            if conversation_id:
                self.conversation_connections[conversation_id].add(connection_id)

            # 更新用户在线状态
            if user_id in self.user_online_status:
                self.user_online_status[user_id].is_online = True
                self.user_online_status[user_id].last_seen = datetime.utcnow()
                self.user_online_status[user_id].connection_count += 1
            else:
                self.user_online_status[user_id] = UserOnlineStatus(
                    user_id=user_id,
                    is_online=True,
                    last_seen=datetime.utcnow(),
                    connection_count=1,
                )

            # 发送连接成功消息
            await self._send_to_connection(
                connection_id,
                {
                    "type": WebSocketMessageType.CONNECT,
                    "data": {
                        "connection_id": connection_id,
                        "user_id": str(user_id),
                        "conversation_id": (
                            str(conversation_id) if conversation_id else None
                        ),
                        "status": "connected",
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            )

            return connection_id

        except Exception as e:
            print(f"WebSocket连接失败: {e}")
            raise

    async def disconnect(self, connection_id: str) -> None:
        """断开WebSocket连接"""
        try:
            if connection_id in self.active_connections:
                # 获取连接信息
                connection_info = self.connection_info.get(connection_id)
                if connection_info:
                    user_id = connection_info.user_id
                    conversation_id = connection_info.conversation_id

                    # 移除连接
                    del self.active_connections[connection_id]
                    del self.connection_info[connection_id]

                    # 更新用户连接映射
                    if user_id in self.user_connections:
                        self.user_connections[user_id].discard(connection_id)
                        if not self.user_connections[user_id]:
                            del self.user_connections[user_id]
                            # 更新用户在线状态
                            if user_id in self.user_online_status:
                                self.user_online_status[user_id].is_online = False
                                self.user_online_status[user_id].connection_count = 0

                    # 更新会话连接映射
                    if (
                        conversation_id
                        and conversation_id in self.conversation_connections
                    ):
                        self.conversation_connections[conversation_id].discard(
                            connection_id
                        )
                        if not self.conversation_connections[conversation_id]:
                            del self.conversation_connections[conversation_id]

                    # 清理输入状态
                    if conversation_id and conversation_id in self.typing_status:
                        if user_id in self.typing_status[conversation_id]:
                            del self.typing_status[conversation_id][user_id]
                        if not self.typing_status[conversation_id]:
                            del self.typing_status[conversation_id]

        except Exception as e:
            print(f"WebSocket断开连接失败: {e}")

    async def send_to_connection(
        self, connection_id: str, message: Dict[str, Any]
    ) -> bool:
        """发送消息到指定连接"""
        try:
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message, default=str))
                return True
            return False
        except Exception as e:
            print(f"发送消息到连接失败: {e}")
            return False

    async def send_to_user(self, user_id: uuid.UUID, message: Dict[str, Any]) -> bool:
        """发送消息到指定用户的所有连接"""
        try:
            if user_id in self.user_connections:
                success_count = 0
                for connection_id in self.user_connections[user_id]:
                    if await self.send_to_connection(connection_id, message):
                        success_count += 1
                return success_count > 0
            return False
        except Exception as e:
            print(f"发送消息到用户失败: {e}")
            return False

    async def broadcast_to_conversation(
        self, conversation_id: uuid.UUID, message: Dict[str, Any]
    ) -> int:
        """广播消息到会话的所有连接"""
        try:
            if conversation_id in self.conversation_connections:
                success_count = 0
                for connection_id in self.conversation_connections[conversation_id]:
                    if await self.send_to_connection(connection_id, message):
                        success_count += 1
                return success_count
            return 0
        except Exception as e:
            print(f"广播消息到会话失败: {e}")
            return 0

    async def broadcast_system_notification(
        self, notification: SystemNotification
    ) -> int:
        """广播系统通知"""
        try:
            success_count = 0

            # 发送给目标用户
            for user_id in notification.target_users:
                if await self.send_to_user(
                    user_id,
                    {
                        "type": WebSocketMessageType.SYSTEM_NOTIFICATION,
                        "data": {
                            "notification_type": notification.notification_type,
                            "title": notification.title,
                            "message": notification.message,
                            "data": notification.data,
                            "timestamp": notification.created_at.isoformat(),
                        },
                    },
                ):
                    success_count += 1

            # 发送给目标会话
            for conversation_id in notification.target_conversations:
                if await self.broadcast_to_conversation(
                    conversation_id,
                    {
                        "type": WebSocketMessageType.SYSTEM_NOTIFICATION,
                        "data": {
                            "notification_type": notification.notification_type,
                            "title": notification.title,
                            "message": notification.message,
                            "data": notification.data,
                            "timestamp": notification.created_at.isoformat(),
                        },
                    },
                ):
                    success_count += 1

            return success_count
        except Exception as e:
            print(f"广播系统通知失败: {e}")
            return 0

    async def send_typing_status(
        self, connection_id: str, conversation_id: uuid.UUID, is_typing: bool
    ) -> bool:
        """发送输入状态"""
        try:
            if connection_id in self.connection_info:
                connection_info = self.connection_info[connection_id]
                user_id = connection_info.user_id

                # 更新输入状态
                if is_typing:
                    self.typing_status[conversation_id][user_id] = TypingStatus(
                        user_id=user_id, conversation_id=conversation_id, is_typing=True
                    )
                else:
                    if (
                        conversation_id in self.typing_status
                        and user_id in self.typing_status[conversation_id]
                    ):
                        del self.typing_status[conversation_id][user_id]

                # 广播输入状态到会话
                await self._broadcast_to_conversation(
                    conversation_id,
                    {
                        "type": (
                            WebSocketMessageType.TYPING_START
                            if is_typing
                            else WebSocketMessageType.TYPING_STOP
                        ),
                        "data": {
                            "user_id": str(user_id),
                            "conversation_id": str(conversation_id),
                            "is_typing": is_typing,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    },
                )

                return True
            return False
        except Exception as e:
            print(f"发送输入状态失败: {e}")
            return False

    async def get_online_users(self) -> List[uuid.UUID]:
        """获取在线用户列表"""
        return [
            user_id
            for user_id, status in self.user_online_status.items()
            if status.is_online
        ]

    async def get_conversation_participants(
        self, conversation_id: uuid.UUID
    ) -> List[uuid.UUID]:
        """获取会话参与者列表"""
        participants = set()
        if conversation_id in self.conversation_connections:
            for connection_id in self.conversation_connections[conversation_id]:
                if connection_id in self.connection_info:
                    participants.add(self.connection_info[connection_id].user_id)
        return list(participants)

    async def get_user_connections(self, user_id: uuid.UUID) -> List[str]:
        """获取用户的所有连接"""
        return list(self.user_connections.get(user_id, set()))

    async def _send_to_connection(
        self, connection_id: str, message: Dict[str, Any]
    ) -> None:
        """内部方法：发送消息到连接"""
        await self.send_to_connection(connection_id, message)

    async def _broadcast_to_conversation(
        self, conversation_id: uuid.UUID, message: Dict[str, Any]
    ) -> None:
        """内部方法：广播消息到会话"""
        await self.broadcast_to_conversation(conversation_id, message)

    def start_cleanup_task(self) -> None:
        """启动清理任务"""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(
                self._cleanup_inactive_connections()
            )

    async def _cleanup_inactive_connections(self) -> None:
        """清理非活跃连接"""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                current_time = datetime.utcnow()
                inactive_connections = []

                for connection_id, connection_info in self.connection_info.items():
                    # 检查连接是否超时
                    if (
                        connection_info.last_pong
                        and (current_time - connection_info.last_pong).total_seconds()
                        > self.connection_timeout
                    ):
                        inactive_connections.append(connection_id)

                # 清理非活跃连接
                for connection_id in inactive_connections:
                    await self.disconnect(connection_id)

            except Exception as e:
                print(f"清理非活跃连接失败: {e}")
                await asyncio.sleep(60)  # 出错时等待1分钟再重试


# 全局连接管理器实例
websocket_manager = ConnectionManager()
