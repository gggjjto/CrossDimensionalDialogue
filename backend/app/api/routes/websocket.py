import json
import uuid
from typing import Dict, Any

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import HTTPBearer

from app.api.deps import get_current_user
from app.models.user import User
from app.services.websocket_manager import websocket_manager
from app.services.websocket_handlers import (
    websocket_message_handler,
    websocket_event_handler,
)
from app.models.websocket import WebSocketMessageType, WebSocketError

router = APIRouter()
security = HTTPBearer()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """WebSocket连接端点"""
    connection_id = str(uuid.uuid4())
    user_id = None

    try:
        # 验证token（简化版本，实际应该使用JWT验证）
        if not token:
            await websocket.close(code=1008, reason="缺少认证token")
            return

        # 这里应该验证JWT token并获取用户ID
        # 为了简化，我们假设token格式为 "user_id:token"
        try:
            user_id_str, _ = token.split(":", 1)
            user_id = uuid.UUID(user_id_str)
        except (ValueError, IndexError):
            await websocket.close(code=1008, reason="无效的认证token")
            return

        # 建立连接
        await websocket_manager.connect(websocket, user_id, connection_id)

        # 处理消息循环
        while True:
            try:
                # 接收消息
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # 处理消息
                await websocket_message_handler.handle_message(
                    websocket, connection_id, user_id, message_data
                )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": WebSocketMessageType.ERROR,
                            "data": {
                                "error_code": "INVALID_JSON",
                                "error_message": "无效的JSON格式",
                                "timestamp": websocket_manager._get_current_timestamp(),
                            },
                        }
                    )
                )
            except Exception as e:
                print(f"WebSocket消息处理错误: {e}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": WebSocketMessageType.ERROR,
                            "data": {
                                "error_code": "INTERNAL_ERROR",
                                "error_message": "内部服务器错误",
                                "timestamp": websocket_manager._get_current_timestamp(),
                            },
                        }
                    )
                )

    except Exception as e:
        print(f"WebSocket连接错误: {e}")
    finally:
        # 断开连接
        await websocket_manager.disconnect(connection_id)


@router.websocket("/ws/{conversation_id}")
async def websocket_conversation_endpoint(
    websocket: WebSocket, conversation_id: str, token: str = None
):
    """特定会话的WebSocket连接端点"""
    connection_id = str(uuid.uuid4())
    user_id = None

    try:
        # 验证token
        if not token:
            await websocket.close(code=1008, reason="缺少认证token")
            return

        try:
            user_id_str, _ = token.split(":", 1)
            user_id = uuid.UUID(user_id_str)
        except (ValueError, IndexError):
            await websocket.close(code=1008, reason="无效的认证token")
            return

        # 验证会话ID
        try:
            conversation_uuid = uuid.UUID(conversation_id)
        except ValueError:
            await websocket.close(code=1008, reason="无效的会话ID")
            return

        # 建立连接
        await websocket_manager.connect(websocket, user_id, connection_id)

        # 自动加入会话
        join_success = await websocket_manager.join_conversation(
            connection_id, conversation_uuid
        )
        if not join_success:
            await websocket.close(code=1008, reason="无法加入会话，可能没有权限")
            return

        # 处理消息循环
        while True:
            try:
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # 处理消息
                await websocket_message_handler.handle_message(
                    websocket, connection_id, user_id, message_data
                )

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": WebSocketMessageType.ERROR,
                            "data": {
                                "error_code": "INVALID_JSON",
                                "error_message": "无效的JSON格式",
                                "timestamp": websocket_manager._get_current_timestamp(),
                            },
                        }
                    )
                )
            except Exception as e:
                print(f"WebSocket消息处理错误: {e}")
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": WebSocketMessageType.ERROR,
                            "data": {
                                "error_code": "INTERNAL_ERROR",
                                "error_message": "内部服务器错误",
                                "timestamp": websocket_manager._get_current_timestamp(),
                            },
                        }
                    )
                )

    except Exception as e:
        print(f"WebSocket连接错误: {e}")
    finally:
        # 断开连接
        await websocket_manager.disconnect(connection_id)


@router.get("/connections")
async def get_connections(current_user: User = Depends(get_current_user)):
    """获取当前用户的连接信息"""
    user_connections = await websocket_manager.get_user_connections(current_user.id)

    connections_info = []
    for connection_id in user_connections:
        connection_info = await websocket_manager.get_connection_info(connection_id)
        if connection_info:
            connections_info.append(
                {
                    "connection_id": connection_id,
                    "status": connection_info.status,
                    "connected_at": connection_info.connected_at.isoformat(),
                    "last_activity": connection_info.last_activity.isoformat(),
                    "active_conversations": [
                        str(conv_id) for conv_id in connection_info.active_conversations
                    ],
                }
            )

    return {
        "code": 0,
        "data": {
            "user_id": str(current_user.id),
            "connections": connections_info,
            "total_connections": len(connections_info),
        },
    }


@router.get("/conversations/{conversation_id}/participants")
async def get_conversation_participants(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """获取会话参与者"""
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会话ID格式"
        )

    participants = await websocket_manager.get_conversation_participants(
        conversation_uuid
    )

    return {
        "code": 0,
        "data": {
            "conversation_id": conversation_id,
            "participants": [str(user_id) for user_id in participants],
            "total_participants": len(participants),
        },
    }


@router.get("/online-users")
async def get_online_users(current_user: User = Depends(get_current_user)):
    """获取在线用户列表"""
    online_users = await websocket_manager.get_online_users()

    return {
        "code": 0,
        "data": {
            "online_users": [str(user_id) for user_id in online_users],
            "total_online": len(online_users),
        },
    }


@router.post("/conversations/{conversation_id}/join")
async def join_conversation_ws(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """加入会话（通过REST API）"""
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会话ID格式"
        )

    # 获取用户的所有连接
    user_connections = await websocket_manager.get_user_connections(current_user.id)

    if not user_connections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户没有活跃的WebSocket连接",
        )

    # 为所有连接加入会话
    success_count = 0
    for connection_id in user_connections:
        if await websocket_manager.join_conversation(connection_id, conversation_uuid):
            success_count += 1

    return {
        "code": 0,
        "data": {
            "conversation_id": conversation_id,
            "joined_connections": success_count,
            "total_connections": len(user_connections),
        },
    }


@router.post("/conversations/{conversation_id}/leave")
async def leave_conversation_ws(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """离开会话（通过REST API）"""
    try:
        conversation_uuid = uuid.UUID(conversation_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="无效的会话ID格式"
        )

    # 获取用户的所有连接
    user_connections = await websocket_manager.get_user_connections(current_user.id)

    if not user_connections:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户没有活跃的WebSocket连接",
        )

    # 为所有连接离开会话
    success_count = 0
    for connection_id in user_connections:
        if await websocket_manager.leave_conversation(connection_id, conversation_uuid):
            success_count += 1

    return {
        "code": 0,
        "data": {
            "conversation_id": conversation_id,
            "left_connections": success_count,
            "total_connections": len(user_connections),
        },
    }


@router.post("/broadcast")
async def broadcast_message(
    message_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """广播消息（管理员功能）"""
    # 检查用户权限
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )

    target_users = message_data.get("target_users", [])
    target_conversations = message_data.get("target_conversations", [])
    message = message_data.get("message", {})

    if not target_users and not target_conversations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="必须指定目标用户或会话"
        )

    sent_count = 0

    # 发送给指定用户
    for user_id_str in target_users:
        try:
            user_id = uuid.UUID(user_id_str)
            if await websocket_manager.send_to_user(user_id, message):
                sent_count += 1
        except ValueError:
            continue

    # 发送给指定会话
    for conversation_id_str in target_conversations:
        try:
            conversation_id = uuid.UUID(conversation_id_str)
            await websocket_manager._broadcast_to_conversation(conversation_id, message)
            sent_count += 1
        except ValueError:
            continue

    return {
        "code": 0,
        "data": {
            "sent_count": sent_count,
            "target_users": len(target_users),
            "target_conversations": len(target_conversations),
        },
    }


# 添加辅助方法到websocket_manager
def _get_current_timestamp():
    """获取当前时间戳"""
    from datetime import datetime

    return datetime.utcnow().isoformat()


# 为websocket_manager添加辅助方法
websocket_manager._get_current_timestamp = _get_current_timestamp
