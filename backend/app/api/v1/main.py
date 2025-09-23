from app.api.routes import (
    items,
    login,
    private,
    users,
    utils,
    conversations,
    dialogue_orchestration,
    multi_character,
    knowledge,
)
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
api_router.include_router(
    dialogue_orchestration.router,
    prefix="/orchestration",
    tags=["dialogue-orchestration"],
)
api_router.include_router(
    multi_character.router,
    prefix="/multi-character",
    tags=["multi-character"],
)
api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["knowledge"],
)

# Only include private routes in local environment


if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
    api_router.include_router(private.router)
    api_router.include_router(private.router)
