import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.services.websocket_manager import ConnectionManager
from app.models.websocket import WebSocketMessageType, SystemNotification


class TestConnectionManager:
    """WebSocket连接管理器测试"""

    @pytest.fixture
    def manager(self):
        return ConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.close = AsyncMock()
        websocket.accept = AsyncMock()

        # 模拟client对象
        mock_client = MagicMock()
        mock_client.host = "127.0.0.1"
        websocket.client = mock_client

        return websocket

    @pytest.mark.asyncio
    async def test_connect(self, manager, mock_websocket):
        """测试连接"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 验证连接被记录
        assert connection_id in manager.active_connections
        assert connection_id in manager.connection_info
        assert manager.connection_info[connection_id].user_id == user_id
        assert manager.connection_info[connection_id].conversation_id == conversation_id

        # 验证用户在线状态
        assert user_id in manager.user_online_status
        assert manager.user_online_status[user_id].is_online
        assert manager.user_online_status[user_id].last_seen is not None

    @pytest.mark.asyncio
    async def test_disconnect(self, manager, mock_websocket):
        """测试断开连接"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 断开连接
        await manager.disconnect(connection_id)

        # 验证连接被移除
        assert connection_id not in manager.active_connections

        # 验证用户在线状态被更新
        assert user_id in manager.user_online_status
        assert not manager.user_online_status[user_id].is_online

    @pytest.mark.asyncio
    async def test_send_to_connection(self, manager, mock_websocket):
        """测试发送消息到连接"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 发送消息
        message = {"type": "test", "data": "test message"}
        success = await manager.send_to_connection(connection_id, message)

        # 验证消息被发送
        assert success
        assert mock_websocket.send_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_send_to_user(self, manager, mock_websocket):
        """测试发送消息到用户"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 发送消息
        message = {"type": "test", "data": "test message"}
        success = await manager.send_to_user(user_id, message)

        # 验证消息被发送
        assert success
        assert mock_websocket.send_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_to_conversation(self, manager, mock_websocket):
        """测试广播消息到会话"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 广播消息
        message = {"type": "test", "data": "test message"}
        success_count = await manager.broadcast_to_conversation(
            conversation_id, message
        )

        # 验证消息被广播
        assert success_count == 1
        assert mock_websocket.send_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_broadcast_system_notification(self, manager, mock_websocket):
        """测试广播系统通知"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 创建系统通知
        notification = SystemNotification(
            notification_type="test",
            title="Test Notification",
            message="This is a test notification",
            target_users=[user_id],
            target_conversations=[conversation_id],
        )

        # 广播通知
        success_count = await manager.broadcast_system_notification(notification)

        # 验证通知被广播（连接消息 + 系统通知）
        assert success_count >= 1
        assert mock_websocket.send_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_send_typing_status(self, manager, mock_websocket):
        """测试发送输入状态"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 发送输入状态
        success = await manager.send_typing_status(connection_id, conversation_id, True)

        # 验证状态被发送
        assert success
        assert mock_websocket.send_text.call_count >= 1

    @pytest.mark.asyncio
    async def test_get_online_users(self, manager, mock_websocket):
        """测试获取在线用户"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 获取在线用户
        online_users = await manager.get_online_users()

        # 验证用户在线
        assert user_id in online_users

    @pytest.mark.asyncio
    async def test_get_conversation_participants(self, manager, mock_websocket):
        """测试获取会话参与者"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 获取会话参与者
        participants = await manager.get_conversation_participants(conversation_id)

        # 验证参与者
        assert user_id in participants

    @pytest.mark.asyncio
    async def test_get_user_connections(self, manager, mock_websocket):
        """测试获取用户连接"""
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 连接
        connection_id = await manager.connect(mock_websocket, user_id, conversation_id)

        # 获取用户连接
        connections = await manager.get_user_connections(user_id)

        # 验证连接
        assert connection_id in connections

    @pytest.mark.asyncio
    async def test_connection_not_found(self, manager):
        """测试连接不存在的情况"""
        # 尝试发送消息到不存在的连接
        success = await manager.send_to_connection("non-existent", {"type": "test"})
        assert not success

    @pytest.mark.asyncio
    async def test_user_not_online(self, manager):
        """测试用户不在线的情况"""
        user_id = uuid.uuid4()

        # 尝试发送消息给不在线的用户
        success = await manager.send_to_user(user_id, {"type": "test"})
        assert not success

    @pytest.mark.asyncio
    async def test_conversation_no_participants(self, manager):
        """测试会话没有参与者的情况"""
        conversation_id = uuid.uuid4()

        # 尝试广播消息到没有参与者的会话
        success_count = await manager.broadcast_to_conversation(
            conversation_id, {"type": "test"}
        )
        assert success_count == 0
