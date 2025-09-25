import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.realtime_service import (
    RealtimeMessageService,
    RealtimePresenceService,
    RealtimeNotificationService,
)
from app.models.conversation import SenderType, ContentType


class TestRealtimeMessageService:
    """实时消息服务测试"""

    @pytest.fixture
    def service(self):
        return RealtimeMessageService()

    @pytest.fixture
    def mock_websocket_manager(self):
        manager = AsyncMock()
        manager._broadcast_to_conversation = AsyncMock()
        return manager

    @pytest.fixture
    def mock_event_handler(self):
        handler = AsyncMock()
        handler.handle_event = AsyncMock()
        return handler

    @pytest.fixture
    def mock_db(self):
        db = MagicMock()
        db.add = MagicMock()
        db.commit = MagicMock()
        db.close = MagicMock()
        return db

    @pytest.fixture
    def mock_conversation(self):
        conversation = MagicMock()
        conversation.message_count = 0
        conversation.last_message_at = None
        conversation.updated_at = datetime.utcnow()
        return conversation

    @pytest.fixture
    def mock_message(self):
        message = MagicMock()
        message.id = uuid.uuid4()
        message.content = "Test message"
        message.content_type = ContentType.TEXT
        message.sender_type = SenderType.USER
        message.sender_id = uuid.uuid4()
        message.message_metadata = {"test": "data"}
        message.created_at = datetime.utcnow()
        return message

    @pytest.mark.asyncio
    async def test_send_message_to_conversation_success(
        self,
        service,
        mock_websocket_manager,
        mock_event_handler,
        mock_db,
        mock_conversation,
        mock_message,
    ):
        """测试成功发送消息到会话"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.websocket_event_handler", mock_event_handler
        ), patch(
            "app.services.realtime_service.get_db"
        ) as mock_get_db, patch(
            "app.services.realtime_service.conversation"
        ) as mock_conversation_crud, patch(
            "app.services.realtime_service.message"
        ) as mock_message_crud:

            # 设置模拟
            mock_get_db.return_value = iter([mock_db])
            mock_conversation_crud.get_by_user_and_id.return_value = mock_conversation
            mock_message_crud.create.return_value = mock_message
            mock_message_crud.MessageCreate = MagicMock

            # 测试数据
            conversation_id = uuid.uuid4()
            sender_id = uuid.uuid4()
            message_data = {
                "content": "Test message",
                "content_type": "text",
                "metadata": {"test": "data"},
            }

            # 执行测试
            result = await service.send_message_to_conversation(
                conversation_id, message_data, sender_id
            )

            # 验证结果
            assert result is True
            mock_message_crud.create.assert_called_once()
            mock_conversation_crud.get_by_user_and_id.assert_called_once()
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_db.close.assert_called_once()
            mock_websocket_manager._broadcast_to_conversation.assert_called_once()
            mock_event_handler.handle_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_to_conversation_failure(
        self, service, mock_websocket_manager, mock_event_handler
    ):
        """测试发送消息到会话失败"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.websocket_event_handler", mock_event_handler
        ), patch(
            "app.services.realtime_service.get_db"
        ) as mock_get_db:

            # 模拟数据库异常
            mock_get_db.side_effect = Exception("Database error")

            # 测试数据
            conversation_id = uuid.uuid4()
            sender_id = uuid.uuid4()
            message_data = {"content": "Test message"}

            # 执行测试
            result = await service.send_message_to_conversation(
                conversation_id, message_data, sender_id
            )

            # 验证结果
            assert result is False

    @pytest.mark.asyncio
    async def test_update_message_in_conversation_success(
        self, service, mock_websocket_manager, mock_event_handler, mock_db, mock_message
    ):
        """测试成功更新会话中的消息"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.websocket_event_handler", mock_event_handler
        ), patch(
            "app.services.realtime_service.get_db"
        ) as mock_get_db, patch(
            "app.services.realtime_service.message"
        ) as mock_message_crud:

            # 设置模拟
            mock_get_db.return_value = iter([mock_db])
            mock_message_crud.get_by_conversation_and_id.return_value = mock_message
            mock_message_crud.update.return_value = mock_message
            mock_message_crud.MessageUpdate = MagicMock

            # 测试数据
            conversation_id = uuid.uuid4()
            message_id = uuid.uuid4()
            user_id = uuid.uuid4()
            updates = {"content": "Updated message"}

            # 执行测试
            result = await service.update_message_in_conversation(
                conversation_id, message_id, updates, user_id
            )

            # 验证结果
            assert result is True
            mock_message_crud.get_by_conversation_and_id.assert_called_once()
            mock_message_crud.update.assert_called_once()
            mock_websocket_manager._broadcast_to_conversation.assert_called_once()
            mock_event_handler.handle_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_message_in_conversation_not_found(
        self, service, mock_websocket_manager, mock_event_handler, mock_db
    ):
        """测试更新不存在的消息"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.websocket_event_handler", mock_event_handler
        ), patch(
            "app.services.realtime_service.get_db"
        ) as mock_get_db, patch(
            "app.services.realtime_service.message"
        ) as mock_message_crud:

            # 设置模拟
            mock_get_db.return_value = iter([mock_db])
            mock_message_crud.get_by_conversation_and_id.return_value = None

            # 测试数据
            conversation_id = uuid.uuid4()
            message_id = uuid.uuid4()
            user_id = uuid.uuid4()
            updates = {"content": "Updated message"}

            # 执行测试
            result = await service.update_message_in_conversation(
                conversation_id, message_id, updates, user_id
            )

            # 验证结果
            assert result is False

    @pytest.mark.asyncio
    async def test_delete_message_from_conversation_success(
        self,
        service,
        mock_websocket_manager,
        mock_event_handler,
        mock_db,
        mock_conversation,
        mock_message,
    ):
        """测试成功删除会话中的消息"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.websocket_event_handler", mock_event_handler
        ), patch(
            "app.services.realtime_service.get_db"
        ) as mock_get_db, patch(
            "app.services.realtime_service.conversation"
        ) as mock_conversation_crud, patch(
            "app.services.realtime_service.message"
        ) as mock_message_crud:

            # 设置模拟
            mock_get_db.return_value = iter([mock_db])
            mock_message_crud.get_by_conversation_and_id.return_value = mock_message
            mock_message_crud.delete.return_value = True
            mock_conversation_crud.get_by_user_and_id.return_value = mock_conversation

            # 测试数据
            conversation_id = uuid.uuid4()
            message_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 执行测试
            result = await service.delete_message_from_conversation(
                conversation_id, message_id, user_id
            )

            # 验证结果
            assert result is True
            mock_message_crud.get_by_conversation_and_id.assert_called_once()
            mock_message_crud.delete.assert_called_once()
            mock_conversation_crud.get_by_user_and_id.assert_called_once()
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()
            mock_websocket_manager._broadcast_to_conversation.assert_called_once()
            mock_event_handler.handle_event.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_typing_status_success(self, service, mock_websocket_manager):
        """测试成功发送输入状态"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            mock_websocket_manager.get_user_connections.return_value = [
                "conn1",
                "conn2",
            ]
            mock_websocket_manager.send_typing_status.return_value = True

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 执行测试
            result = await service.send_typing_status(conversation_id, user_id, True)

            # 验证结果
            assert result is True
            mock_websocket_manager.get_user_connections.assert_called_once_with(user_id)
            assert mock_websocket_manager.send_typing_status.call_count == 2

    @pytest.mark.asyncio
    async def test_send_typing_status_no_connections(
        self, service, mock_websocket_manager
    ):
        """测试发送输入状态时没有连接"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            mock_websocket_manager.get_user_connections.return_value = []

            # 测试数据
            conversation_id = uuid.uuid4()
            user_id = uuid.uuid4()

            # 执行测试
            result = await service.send_typing_status(conversation_id, user_id, True)

            # 验证结果
            assert result is False


class TestRealtimePresenceService:
    """实时在线状态服务测试"""

    @pytest.fixture
    def service(self):
        return RealtimePresenceService()

    @pytest.fixture
    def mock_websocket_manager(self):
        manager = AsyncMock()
        manager.user_online_status = {}
        manager.get_online_users = AsyncMock(return_value=[])
        manager.get_conversation_participants = AsyncMock(return_value=[])
        manager.get_user_connections = AsyncMock(return_value=[])
        return manager

    @pytest.mark.asyncio
    async def test_get_user_online_status(self, service, mock_websocket_manager):
        """测试获取用户在线状态"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            user_id = uuid.uuid4()
            mock_websocket_manager.user_online_status[user_id] = MagicMock()

            # 执行测试
            result = await service.get_user_online_status(user_id)

            # 验证结果
            assert result == mock_websocket_manager.user_online_status[user_id]

    @pytest.mark.asyncio
    async def test_get_online_users(self, service, mock_websocket_manager):
        """测试获取在线用户列表"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            online_users = [uuid.uuid4(), uuid.uuid4()]
            mock_websocket_manager.get_online_users.return_value = online_users

            # 执行测试
            result = await service.get_online_users()

            # 验证结果
            assert result == online_users

    @pytest.mark.asyncio
    async def test_get_conversation_participants(self, service, mock_websocket_manager):
        """测试获取会话参与者"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            conversation_id = uuid.uuid4()
            participants = [uuid.uuid4(), uuid.uuid4()]
            mock_websocket_manager.get_conversation_participants.return_value = (
                participants
            )

            # 执行测试
            result = await service.get_conversation_participants(conversation_id)

            # 验证结果
            assert result == participants

    @pytest.mark.asyncio
    async def test_is_user_online(self, service, mock_websocket_manager):
        """测试检查用户是否在线"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            user_id = uuid.uuid4()
            mock_websocket_manager.user_online_status[user_id] = MagicMock()

            # 执行测试
            result = await service.is_user_online(user_id)

            # 验证结果
            assert result is True

    @pytest.mark.asyncio
    async def test_get_user_connections(self, service, mock_websocket_manager):
        """测试获取用户连接"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ):
            # 设置模拟
            user_id = uuid.uuid4()
            connections = ["conn1", "conn2"]
            mock_websocket_manager.get_user_connections.return_value = connections

            # 执行测试
            result = await service.get_user_connections(user_id)

            # 验证结果
            assert result == connections


class TestRealtimeNotificationService:
    """实时通知服务测试"""

    @pytest.fixture
    def service(self):
        return RealtimeNotificationService()

    @pytest.fixture
    def mock_websocket_manager(self):
        manager = AsyncMock()
        manager.get_conversation_participants = AsyncMock(return_value=[])
        manager.send_to_user = AsyncMock()
        return manager

    @pytest.fixture
    def mock_realtime_service(self):
        service = AsyncMock()
        service.send_system_notification = AsyncMock()
        return service

    @pytest.mark.asyncio
    async def test_send_message_notification(
        self, service, mock_websocket_manager, mock_realtime_service
    ):
        """测试发送消息通知"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.realtime_message_service",
            mock_realtime_service,
        ):

            # 设置模拟
            conversation_id = uuid.uuid4()
            participants = [uuid.uuid4(), uuid.uuid4()]
            mock_websocket_manager.get_conversation_participants.return_value = (
                participants
            )

            # 测试数据
            message_id = uuid.uuid4()
            sender_id = uuid.uuid4()
            content = "Test message"

            # 执行测试
            await service.send_message_notification(
                conversation_id, message_id, sender_id, content
            )

            # 验证结果
            mock_websocket_manager.get_conversation_participants.assert_called_once_with(
                conversation_id
            )
            assert mock_websocket_manager.send_to_user.call_count == 2

    @pytest.mark.asyncio
    async def test_send_conversation_notification(
        self, service, mock_websocket_manager, mock_realtime_service
    ):
        """测试发送会话通知"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.realtime_message_service",
            mock_realtime_service,
        ):

            # 测试数据
            conversation_id = uuid.uuid4()
            notification_type = "test"
            title = "Test Notification"
            message = "This is a test notification"
            data = {"test": "data"}

            # 执行测试
            await service.send_conversation_notification(
                conversation_id, notification_type, title, message, data
            )

            # 验证结果
            mock_realtime_service.send_system_notification.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_user_notification(
        self, service, mock_websocket_manager, mock_realtime_service
    ):
        """测试发送用户通知"""
        with patch(
            "app.services.realtime_service.websocket_manager", mock_websocket_manager
        ), patch(
            "app.services.realtime_service.realtime_message_service",
            mock_realtime_service,
        ):

            # 测试数据
            user_id = uuid.uuid4()
            notification_type = "test"
            title = "Test Notification"
            message = "This is a test notification"
            data = {"test": "data"}

            # 执行测试
            await service.send_user_notification(
                user_id, notification_type, title, message, data
            )

            # 验证结果
            mock_realtime_service.send_system_notification.assert_called_once()
