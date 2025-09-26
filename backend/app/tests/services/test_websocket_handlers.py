import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.websocket_handlers import websocket_event_handler
from app.models.websocket import WebSocketMessageType, SystemNotification


class TestWebSocketEventHandlers:
    """WebSocket事件处理器测试"""

    @pytest.fixture
    def mock_websocket_manager(self):
        manager = AsyncMock()
        manager.send_to_user = AsyncMock(return_value=True)
        manager.broadcast_to_conversation = AsyncMock(return_value=1)
        manager.broadcast_system_notification = AsyncMock(return_value=1)
        return manager

    @pytest.fixture
    def mock_realtime_service(self):
        service = AsyncMock()
        service.send_message_to_conversation = AsyncMock(return_value=True)
        service.update_message_in_conversation = AsyncMock(return_value=True)
        service.delete_message_from_conversation = AsyncMock(return_value=True)
        service.send_typing_status = AsyncMock(return_value=True)
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
    async def test_handle_message_send(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理发送消息事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "content": "Hello, world!",
                "content_type": "text",
                "sender_id": str(uuid.uuid4()),
                "metadata": {"test": "data"},
            }

            result = await websocket_event_handler.handle_event(
                "message_send", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.send_message_to_conversation.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_message_update(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理更新消息事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "updates": {"content": "Updated message"},
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "message_update", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.update_message_in_conversation.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_message_delete(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理删除消息事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "message_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "message_delete", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.delete_message_from_conversation.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_typing_start(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理开始输入事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "typing_start", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.send_typing_status.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_typing_stop(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理停止输入事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "typing_stop", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.send_typing_status.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_conversation_created(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理会话创建事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "conversation_created", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.notify_conversation_created.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_conversation_updated(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理会话更新事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
                "updates": {"title": "New Title"},
            }

            result = await websocket_event_handler.handle_event(
                "conversation_updated", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.notify_conversation_updated.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_conversation_deleted(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理会话删除事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "user_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "conversation_deleted", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.notify_conversation_deleted.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_system_notification(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理系统通知事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {
                "notification_type": "test",
                "title": "Test Notification",
                "message": "This is a test notification",
                "target_users": [str(uuid.uuid4())],
                "target_conversations": [str(uuid.uuid4())],
                "data": {"test": "data"},
            }

            result = await websocket_event_handler.handle_event(
                "system_notification", event_data
            )

            # 验证实时消息服务被调用
            mock_realtime_service.send_system_notification.assert_called_once()
            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_handle_unknown_event(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理未知事件"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            event_data = {"test": "data"}

            result = await websocket_event_handler.handle_event(
                "unknown_event", event_data
            )

            # 验证返回错误
            assert result["success"] is False
            assert "Unknown event type" in result["error"]

    @pytest.mark.asyncio
    async def test_handle_event_with_exception(
        self, mock_websocket_manager, mock_realtime_service
    ):
        """测试处理事件时发生异常"""
        with patch(
            "app.services.websocket_handlers.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.websocket_handlers.realtime_message_service",
            mock_realtime_service,
        ):

            # 模拟服务抛出异常
            mock_realtime_service.send_message_to_conversation.side_effect = Exception(
                "Test error"
            )

            event_data = {
                "conversation_id": str(uuid.uuid4()),
                "content": "Hello, world!",
                "content_type": "text",
                "sender_id": str(uuid.uuid4()),
            }

            result = await websocket_event_handler.handle_event(
                "message_send", event_data
            )

            # 验证返回错误
            assert result["success"] is False
            assert "Test error" in result["error"]
