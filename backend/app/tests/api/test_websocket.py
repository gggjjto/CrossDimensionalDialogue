import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.websocket import WebSocketMessageType


class TestWebSocketAPI:
    """WebSocket API测试"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.fixture
    def mock_websocket_manager(self):
        manager = AsyncMock()
        manager.connect = AsyncMock(return_value="test-connection-id")
        manager.disconnect = AsyncMock()
        manager.send_to_connection = AsyncMock(return_value=True)
        manager.send_to_user = AsyncMock(return_value=True)
        manager.broadcast_to_conversation = AsyncMock(return_value=1)
        manager.broadcast_system_notification = AsyncMock(return_value=1)
        manager.send_typing_status = AsyncMock(return_value=True)
        manager.get_online_users = AsyncMock(return_value=[])
        manager.get_conversation_participants = AsyncMock(return_value=[])
        manager.get_user_connections = AsyncMock(return_value=[])
        return manager

    @pytest.fixture
    def mock_realtime_service(self):
        service = AsyncMock()
        service.send_message_to_conversation = AsyncMock(return_value=True)
        service.update_message_in_conversation = AsyncMock(return_value=True)
        service.delete_message_from_conversation = AsyncMock(return_value=True)
        service.send_typing_status = AsyncMock(return_value=True)
        service.notify_conversation_created = AsyncMock()
        service.notify_conversation_updated = AsyncMock()
        service.notify_conversation_deleted = AsyncMock()
        service.send_system_notification = AsyncMock(return_value=1)
        return service

    @pytest.fixture
    def mock_presence_service(self):
        service = AsyncMock()
        service.get_user_online_status = AsyncMock()
        service.get_online_users = AsyncMock(return_value=[])
        service.get_conversation_participants = AsyncMock(return_value=[])
        service.is_user_online = AsyncMock(return_value=True)
        service.get_user_connections = AsyncMock(return_value=[])
        return service

    @pytest.fixture
    def mock_notification_service(self):
        service = AsyncMock()
        service.send_message_notification = AsyncMock()
        service.send_conversation_notification = AsyncMock()
        service.send_user_notification = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_websocket_connection_success(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket连接成功"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 验证连接管理器被调用
                mock_websocket_manager.connect.assert_called_once()

                # 发送测试消息
                test_message = {
                    "type": WebSocketMessageType.MESSAGE_SEND,
                    "data": {
                        "content": "Hello, world!",
                        "content_type": "text",
                        "metadata": {"test": "data"},
                    },
                }
                websocket.send_json(test_message)

                # 验证实时消息服务被调用
                mock_realtime_service.send_message_to_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_connection_invalid_user_id(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket连接时无效的用户ID"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            invalid_user_id = "invalid-uuid"

            # 尝试连接WebSocket
            with pytest.raises(Exception):  # 应该抛出异常
                with client.websocket_connect(
                    f"/api/v1/conversations/{conversation_id}/ws?user_id={invalid_user_id}"
                ) as websocket:
                    pass

    @pytest.mark.asyncio
    async def test_websocket_connection_invalid_conversation_id(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket连接时无效的会话ID"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            invalid_conversation_id = "invalid-uuid"
            user_id = uuid.uuid4()

            # 尝试连接WebSocket
            with pytest.raises(Exception):  # 应该抛出异常
                with client.websocket_connect(
                    f"/api/v1/conversations/{invalid_conversation_id}/ws?user_id={user_id}"
                ) as websocket:
                    pass

    @pytest.mark.asyncio
    async def test_websocket_message_send(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket发送消息"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 发送消息
                message = {
                    "type": WebSocketMessageType.MESSAGE_SEND,
                    "data": {
                        "content": "Hello, world!",
                        "content_type": "text",
                        "metadata": {"test": "data"},
                    },
                }
                websocket.send_json(message)

                # 验证实时消息服务被调用
                mock_realtime_service.send_message_to_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_message_update(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket更新消息"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()
            message_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 更新消息
                message = {
                    "type": WebSocketMessageType.MESSAGE_UPDATE,
                    "data": {
                        "message_id": str(message_id),
                        "updates": {"content": "Updated message"},
                    },
                }
                websocket.send_json(message)

                # 验证实时消息服务被调用
                mock_realtime_service.update_message_in_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_message_delete(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket删除消息"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()
            message_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 删除消息
                message = {
                    "type": WebSocketMessageType.MESSAGE_DELETE,
                    "data": {"message_id": str(message_id)},
                }
                websocket.send_json(message)

                # 验证实时消息服务被调用
                mock_realtime_service.delete_message_from_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_typing_start(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket开始输入"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 开始输入
                message = {"type": WebSocketMessageType.TYPING_START, "data": {}}
                websocket.send_json(message)

                # 验证实时消息服务被调用
                mock_realtime_service.send_typing_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_typing_stop(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket停止输入"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 停止输入
                message = {"type": WebSocketMessageType.TYPING_STOP, "data": {}}
                websocket.send_json(message)

                # 验证实时消息服务被调用
                mock_realtime_service.send_typing_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_websocket_unknown_message_type(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket未知消息类型"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 模拟WebSocket连接
            with client.websocket_connect(
                f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
            ) as websocket:
                # 发送未知消息类型
                message = {"type": "unknown_type", "data": {}}
                websocket.send_json(message)

                # 验证没有服务被调用
                mock_realtime_service.send_message_to_conversation.assert_not_called()
                mock_realtime_service.update_message_in_conversation.assert_not_called()
                mock_realtime_service.delete_message_from_conversation.assert_not_called()
                mock_realtime_service.send_typing_status.assert_not_called()

    @pytest.mark.asyncio
    async def test_websocket_connection_error(
        self,
        client,
        mock_websocket_manager,
        mock_realtime_service,
        mock_presence_service,
        mock_notification_service,
    ):
        """测试WebSocket连接错误"""
        with patch(
            "app.api.routes.websocket.websocket_manager", mock_websocket_manager
        ), patch(
            "app.api.routes.websocket.realtime_message_service", mock_realtime_service
        ), patch(
            "app.api.routes.websocket.realtime_presence_service", mock_presence_service
        ), patch(
            "app.api.routes.websocket.realtime_notification_service",
            mock_notification_service,
        ):

            # 模拟连接管理器抛出异常
            mock_websocket_manager.connect.side_effect = Exception("Connection error")

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 尝试连接WebSocket
            with pytest.raises(Exception):  # 应该抛出异常
                with client.websocket_connect(
                    f"/api/v1/conversations/{conversation_id}/ws?user_id={user_id}"
                ) as websocket:
                    pass
