from app.api.routes import (
    characters,
    conversations,
    dialogue_orchestration,
    image_file_message,
    items,
    knowledge,
    login,
    multi_character,
    private,
    storage,
    users,
    utils,
    voice,
    voice_websocket,
    websocket,
)
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()

# 认证相关
api_router.include_router(login.router)

# 用户管理
api_router.include_router(users.router)

# 角色管理
api_router.include_router(characters.router)

# 对话管理
api_router.include_router(conversations.router)
api_router.include_router(dialogue_orchestration.router)
api_router.include_router(multi_character.router)

# 语音处理
api_router.include_router(voice.router)
api_router.include_router(voice_websocket.router)

# 文件存储
api_router.include_router(storage.router)

# 文件消息
api_router.include_router(image_file_message.router)

# WebSocket连接
api_router.include_router(websocket.router)

# 工具和项目
api_router.include_router(utils.router)
api_router.include_router(items.router)

# 知识库（可选）
# api_router.include_router(knowledge.router)

# 仅本地环境包含的私有路由
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
