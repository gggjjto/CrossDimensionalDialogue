"""
多角色管理API路由
"""

import uuid
import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.conversation import MultiCharacterConversation, ConversationSettings
from app.models.character import Character
from app.services.multi_character_service import multi_character_service
from app.crud.conversation import conversation as conversation_crud

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/conversations/{conversation_id}/characters/{character_id}",
    status_code=status.HTTP_201_CREATED,
    summary="添加角色到多角色会话",
    description="将指定角色添加到多角色会话中",
)
async def add_character_to_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    character_id: uuid.UUID,
    priority: int = 1,
) -> Dict[str, Any]:
    """
    添加角色到多角色会话
    """
    try:
        # 检查会话是否存在且用户有权限
        db_conversation = conversation_crud.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 添加角色到会话
        multi_char_conv = multi_character_service.add_character_to_conversation(
            db, conversation_id, character_id, priority
        )

        return {
            "success": True,
            "message": "角色已添加到会话",
            "multi_character_conversation": {
                "id": multi_char_conv.id,
                "conversation_id": multi_char_conv.conversation_id,
                "character_id": multi_char_conv.character_id,
                "priority": multi_char_conv.priority,
                "is_active": multi_char_conv.is_active,
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"添加角色到会话失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="添加角色到会话失败",
        )


@router.delete(
    "/conversations/{conversation_id}/characters/{character_id}",
    status_code=status.HTTP_200_OK,
    summary="从多角色会话中移除角色",
    description="从多角色会话中移除指定角色",
)
async def remove_character_from_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    character_id: uuid.UUID,
) -> Dict[str, Any]:
    """
    从多角色会话中移除角色
    """
    try:
        # 检查会话是否存在且用户有权限
        db_conversation = conversation_crud.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 移除角色
        success = multi_character_service.remove_character_from_conversation(
            db, conversation_id, character_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="角色不在会话中"
            )

        return {"success": True, "message": "角色已从会话中移除"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"从会话中移除角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="从会话中移除角色失败",
        )


@router.get(
    "/conversations/{conversation_id}/characters",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="获取会话中的所有角色",
    description="获取指定会话中的所有角色信息",
)
async def get_conversation_characters(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    active_only: bool = True,
) -> List[Dict[str, Any]]:
    """
    获取会话中的所有角色
    """
    try:
        # 检查会话是否存在且用户有权限
        db_conversation = conversation_crud.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 获取会话中的角色
        characters = multi_character_service.get_conversation_characters(
            db, conversation_id, active_only
        )

        # 构建响应数据
        result = []
        for char_conv in characters:
            character = db.get(Character, char_conv.character_id)
            if character:
                result.append(
                    {
                        "multi_character_id": char_conv.id,
                        "character_id": character.id,
                        "character_name": character.name,
                        "character_bio": character.short_bio,
                        "priority": char_conv.priority,
                        "is_active": char_conv.is_active,
                        "response_count": char_conv.response_count,
                        "last_response_at": char_conv.last_response_at,
                        "created_at": char_conv.created_at,
                    }
                )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取会话角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="获取会话角色失败"
        )


@router.put(
    "/conversations/{conversation_id}/characters/{character_id}/priority",
    status_code=status.HTTP_200_OK,
    summary="更新角色优先级",
    description="更新指定角色在会话中的优先级",
)
async def update_character_priority(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    character_id: uuid.UUID,
    priority: int,
) -> Dict[str, Any]:
    """
    更新角色优先级
    """
    try:
        # 检查会话是否存在且用户有权限
        db_conversation = conversation_crud.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 验证优先级范围
        if priority < 1 or priority > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="优先级必须在1-10之间"
            )

        # 更新优先级
        success = multi_character_service.update_character_priority(
            db, conversation_id, character_id, priority
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="角色不在会话中"
            )

        return {"success": True, "message": f"角色优先级已更新为 {priority}"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新角色优先级失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新角色优先级失败",
        )


@router.post(
    "/conversations/{conversation_id}/select-character",
    status_code=status.HTTP_200_OK,
    summary="选择回复角色",
    description="根据用户消息和策略选择最适合回复的角色",
)
async def select_responding_character(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    user_message: str,
) -> Dict[str, Any]:
    """
    选择回复角色
    """
    try:
        # 检查会话是否存在且用户有权限
        db_conversation = conversation_crud.get_by_user_and_id(
            db, id=conversation_id, user_id=current_user.id
        )
        if not db_conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
            )

        # 获取会话设置
        settings = ConversationSettings.parse_obj(db_conversation.settings or {})

        # 选择回复角色
        selected_character = multi_character_service.select_responding_character(
            db, conversation_id, user_message, settings
        )

        if not selected_character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="没有找到合适的角色"
            )

        return {
            "success": True,
            "selected_character": {
                "id": selected_character.id,
                "name": selected_character.name,
                "bio": selected_character.short_bio,
                "persona": selected_character.persona_text,
            },
            "strategy": settings.character_response_strategy.value,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选择回复角色失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="选择回复角色失败"
        )
