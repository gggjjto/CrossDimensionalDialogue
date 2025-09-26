from app.api.routes import (
    characters,
    conversations,
    dialogue_orchestration,
    image,
    items,
    login,
    private,
    users,
    utils,
    voice_processing,
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
api_router.include_router(image.router)

# 语音处理
api_router.include_router(voice_processing.router)

# 工具和项目
api_router.include_router(utils.router)
api_router.include_router(items.router)

# 仅本地环境包含的私有路由
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
