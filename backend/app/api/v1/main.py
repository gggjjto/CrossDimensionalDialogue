from app.api.routes import items, login, private, users, utils, conversations
from app.core.config import settings
from fastapi import APIRouter

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(items.router)
api_router.include_router(
    conversations.router, prefix="/conversations", tags=["conversations"]
)

# Only include private routes in local environment


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
    api_router.include_router(private.router)
    api_router.include_router(private.router)
