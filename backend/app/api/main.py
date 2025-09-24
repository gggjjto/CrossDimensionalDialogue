from fastapi import APIRouter
from app.api.routes.characters import characters
from app.api.routes.conversations import conversations
from app.api.routes.users import users
from app.api.routes.login import login
from app.api.routes.utils import utils
from app.api.routes.dialogue import dialogue_orchestration
from app.api.routes.image import image
from app.api.routes.voice import voice_catalog, voice_processing

from app.api.routes import items, private
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

# 语音处理
api_router.include_router(voice_catalog.router)
api_router.include_router(voice_processing.router)

# 工具和项目
api_router.include_router(utils.router)
api_router.include_router(items.router)

# 仅本地环境包含的私有路由
if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
