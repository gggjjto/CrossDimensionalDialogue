from fastapi import APIRouter
from app.api.routes.characters import characters
from app.api.routes.conversations import conversations
from app.api.routes.users import users
from app.api.routes.login import login
from app.api.routes.utils import utils
from app.api.routes.dialogue import dialogue_orchestration
from app.api.routes.image import image

from app.api.routes import (
    items,
    private
)
from app.core.config import settings

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
# api_router.include_router(multi_character.router)         # 暂时注释

# 语音处理
# api_router.include_router(voice.router)  # 暂时注释
# api_router.include_router(voice_websocket.router)         # 暂时注释

# 文件存储
# api_router.include_router(storage.router)  # 暂时注释

# 文件消息
# api_router.include_router(image_file_message.router)     # 暂时注释

# WebSocket连接
# api_router.include_router(websocket.router)              # 暂时注释

# 工具和项目
api_router.include_router(utils.router)
api_router.include_router(items.router)

# 知识库（可选）
# api_router.include_router(knowledge.router)

# 仅本地环境包含的私有路由
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
