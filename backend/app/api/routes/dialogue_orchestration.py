"""
对话编排API路由
"""

import uuid
import logging
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.dialogue_orchestration import (
    SendMessageRequest,
    SendMessageResponse,
    ConversationContextResponse,
    UpdateConversationSettingsRequest,
    ConversationSettingsResponse,
    MessageInfo,
)
from app.core.config import settings
from app.models.conversation import ConversationSettings
from app.services.dialogue_orchestration_service import dialogue_orchestration_service
from app.crud.conversation import conversation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/conversations/{conversation_id}/send-message",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    request: SendMessageRequest,
) -> SendMessageResponse:
    """
    发送消息并获取角色回复

    Args:
        db: 数据库会话
        current_user: 当前用户
        conversation_id: 会话ID
        request: 发送消息请求

    Returns:
        SendMessageResponse: 发送消息响应
    """
    try:
        # 处理用户消息
        result = await dialogue_orchestration_service.process_user_message(
            db=db,
            conversation_id=conversation_id,
            user_message=request.message,
            user_id=current_user.id,
            settings=request.settings,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["error"],
            )

        return SendMessageResponse(
            success=True,
            user_message_id=result["user_message"].id,
            character_message_id=result["character_message"].id,
            character_response=result["character_response"].content,
            audio_url=result["audio_url"],
            usage=result["character_response"].usage,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"发送消息失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="发送消息失败"
        )


@router.get(
    "/conversations/{conversation_id}/context",
    response_model=ConversationContextResponse,
)
async def get_conversation_context(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    limit: int = 10,
) -> ConversationContextResponse:
    """
    获取会话上下文

    Args:
        db: 数据库会话
        current_user: 当前用户
        conversation_id: 会话ID
        limit: 消息数量限制

    Returns:
        ConversationContextResponse: 会话上下文响应
    """
    try:
        context = await dialogue_orchestration_service.get_conversation_context(
            db=db, conversation_id=conversation_id, user_id=current_user.id, limit=limit
        )

        # 转换消息格式
        recent_messages = []
        for msg in context["recent_messages"]:
            sender_name = None
            if msg.sender_type == "user":
                sender_name = current_user.email.split("@")[0]  # 使用邮箱前缀作为用户名
            elif msg.sender_type == "character":
                sender_name = (
                    context["character"].name if context["character"] else "角色"
                )

            recent_messages.append(
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender_type": msg.sender_type,
                    "sender_name": sender_name,
                    "created_at": msg.created_at,
                }
            )

        return ConversationContextResponse(
            conversation_id=conversation_id,
            character_name=(
                context["character"].name if context["character"] else "未知角色"
            ),
            character_bio=(
                context["character"].short_bio if context["character"] else None
            ),
            recent_messages=recent_messages,
            message_count=context["message_count"],
            context_window_size=context["context_window_size"],
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"获取会话上下文失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取会话上下文失败",
        )


@router.put(
    "/conversations/{conversation_id}/settings",
    response_model=ConversationSettingsResponse,
)
async def update_conversation_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    request: UpdateConversationSettingsRequest,
) -> ConversationSettingsResponse:
    """
    更新会话设置

    Args:
        db: 数据库会话
        current_user: 当前用户
        conversation_id: 会话ID
        request: 更新设置请求

    Returns:
        ConversationSettingsResponse: 会话设置响应
    """
    try:
        # 获取会话
        db_conversation = conversation.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 获取当前设置
        current_settings = ConversationSettings()
        if db_conversation.settings:
            # 从现有设置中更新
            current_settings_dict = db_conversation.settings
            for field, value in request.dict(exclude_unset=True).items():
                if value is not None:
                    current_settings_dict[field] = value
            current_settings = ConversationSettings(**current_settings_dict)
        else:
            # 创建新设置
            current_settings = ConversationSettings(**request.dict(exclude_unset=True))

        # 更新会话设置
        db_conversation.settings = current_settings.dict()
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)

        return ConversationSettingsResponse(
            conversation_id=conversation_id,
            settings=current_settings,
            updated_at=db_conversation.updated_at,
        )

    except Exception as e:
        logger.error(f"更新会话设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新会话设置失败"
        )


@router.get(
    "/conversations/{conversation_id}/settings",
    response_model=ConversationSettingsResponse,
)
async def get_conversation_settings(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
) -> ConversationSettingsResponse:
    """
    获取会话设置

    Args:
        db: 数据库会话
        current_user: 当前用户
        conversation_id: 会话ID

    Returns:
        ConversationSettingsResponse: 会话设置响应
    """
    try:
        # 获取会话
        db_conversation = conversation.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 获取设置
        settings = ConversationSettings()
        if db_conversation.settings:
            settings = ConversationSettings(**db_conversation.settings)

        return ConversationSettingsResponse(
            conversation_id=conversation_id,
            settings=settings,
            updated_at=db_conversation.updated_at,
        )

    except Exception as e:
        logger.error(f"获取会话设置失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取会话设置失败"
        )


@router.get("/models")
async def get_available_models():
    """
    获取可用的LLM模型列表

    Returns:
        Dict[str, Any]: 可用模型信息
    """
    try:
        models = {
            "openai": {
                "provider": "openai",
                "model": settings.OPENAI_MODEL,
                "available": bool(settings.OPENAI_API_KEY),
                "description": "OpenAI GPT模型",
            },
            "deepseek": {
                "provider": "deepseek",
                "model": settings.DEEPSEEK_MODEL,
                "available": bool(settings.DEEPSEEK_API_KEY),
                "description": "DeepSeek Chat模型",
            },
            "qwen": {
                "provider": "qwen",
                "model": settings.QWEN_MODEL,
                "available": bool(settings.QWEN_API_KEY),
                "description": "阿里千问模型",
            },
        }

        return {
            "models": models,
            "default_provider": settings.LLM_PROVIDER,
            "total_available": sum(
                1 for model in models.values() if model["available"]
            ),
        }

    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取模型列表失败"
        )
