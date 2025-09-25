import uuid
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from app.crud.character import character
from app.api.deps import get_db, get_current_user
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)
from app.crud.conversation import (
    conversation,
    message,
    user_conversation_limit,
)
from app.models.user import User
from app.schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationPublic,
    ConversationWithDetails,
    ConversationListResponse,
    ConversationSearchRequest,
    MessageCreate,
    MessagePublic,
    MessageListResponse,
    SenderType,
    ContentType,
)
from app.models.conversation import ConversationStatus

router = APIRouter(prefix="/conversations", tags=["conversations"])


# 会话管理端点
@router.post(
    "/", response_model=ConversationPublic, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_in: ConversationCreate,
) -> ConversationPublic:
    """创建会话"""
    # 验证角色是否存在
    if conversation_in.character_id:
        character_obj = character.get(db, id=conversation_in.character_id)
        if not character_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色不存在: {conversation_in.character_id}",
            )

    # 检查用户会话数量限制
    user_conversation_count = conversation.get_user_conversation_count(
        db, user_id=current_user.id
    )
    # max_conversations_limit = user_conversation_limit.get_by_user_and_type(
    #     db, user_id=current_user.id, limit_type="max_conversations"
    # )
    # 目前最大会话数量限制为10
    max_conversations_limit = settings.MAX_CONVERSATIONS_LIMIT

    if max_conversations_limit and user_conversation_count > max_conversations_limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"已达到最大会话数量限制: {max_conversations_limit.limit_value}",
        )

    # 创建会话
    db_conversation = conversation.create(
        db, obj_in=conversation_in, user_id=current_user.id
    )

    return ConversationPublic.from_orm(db_conversation)


@router.get("/", response_model=ConversationListResponse)
async def get_conversations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    status: Optional[str] = Query(None, description="会话状态过滤"),
    character_id: Optional[uuid.UUID] = Query(None, description="角色ID过滤"),
    order_by: str = Query("last_message_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
) -> ConversationListResponse:
    """获取会话列表"""
    # 转换状态参数
    conversation_status = None
    if status:
        try:
            conversation_status = ConversationStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的会话状态: {status}",
            )

    # 验证排序参数
    if order_by not in ["created_at", "last_message_at", "updated_at", "title"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="不支持的排序字段"
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="排序方向必须是asc或desc"
        )

    conversations, total = conversation.get_multi(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=conversation_status,
        character_id=character_id,
        order_by=order_by,
        order=order,
    )

    # 转换为响应格式
    conversation_list = []
    for conv in conversations:
        conv_dict = ConversationPublic.from_orm(conv).dict()
        conv_dict["character"] = conv.character
        # conv_dict["user"] = conv.user
        conversation_list.append(ConversationWithDetails(**conv_dict))

    return ConversationListResponse(
        conversations=conversation_list,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{conversation_id}", response_model=ConversationWithDetails)
async def get_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
) -> ConversationWithDetails:
    """获取会话详情"""
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 转换为响应格式
    conv_dict = ConversationPublic.from_orm(db_conversation).dict()
    conv_dict["character"] = db_conversation.character
    conv_dict["user"] = db_conversation.user

    return ConversationWithDetails(**conv_dict)


@router.put("/{conversation_id}", response_model=ConversationPublic)
async def update_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    conversation_in: ConversationUpdate,
) -> ConversationPublic:
    """更新会话"""
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 验证角色是否存在（如果提供了character_id）
    if conversation_in.character_id:
        from app.crud import character

        character_obj = character.get(db, id=conversation_in.character_id)
        if not character_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"角色不存在: {conversation_in.character_id}",
            )

    # 更新会话
    db_conversation = conversation.update(
        db, db_obj=db_conversation, obj_in=conversation_in
    )

    return ConversationPublic.from_orm(db_conversation)


@router.delete("/{conversation_id}", response_model=ConversationPublic)
async def delete_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
) -> ConversationPublic:
    """删除会话"""
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 软删除会话
    db_conversation = conversation.delete(
        db, id=conversation_id, user_id=current_user.id
    )

    return ConversationPublic.from_orm(db_conversation)


@router.post("/search", response_model=ConversationListResponse)
async def search_conversations(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search_params: ConversationSearchRequest,
) -> ConversationListResponse:
    """搜索会话"""
    conversations, total = conversation.search(
        db, user_id=current_user.id, search_params=search_params
    )

    # 转换为响应格式
    conversation_list = []
    for conv in conversations:
        conv_dict = ConversationPublic.from_orm(conv).dict()
        conv_dict["character"] = conv.character
        conv_dict["user"] = conv.user
        conversation_list.append(ConversationWithDetails(**conv_dict))

    return ConversationListResponse(
        conversations=conversation_list,
        total=total,
        skip=search_params.skip,
        limit=search_params.limit,
    )


# 消息管理端点
@router.post(
    "/{conversation_id}/messages",
    response_model=MessagePublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    message_in: MessageCreate,
) -> MessagePublic:
    """发送消息"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 检查用户消息限制
    daily_limit = user_conversation_limit.get_by_user_and_type(
        db, user_id=current_user.id, limit_type="daily_messages"
    )

    if daily_limit:
        # 重置限制如果需要
        daily_limit = user_conversation_limit.reset_if_needed(db, db_obj=daily_limit)

        if daily_limit.current_value >= daily_limit.limit_value:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"已达到每日消息数量限制: {daily_limit.limit_value}",
            )

    # 设置发送者信息
    if message_in.sender_type == SenderType.USER:
        message_in.sender_id = current_user.id

    # 创建消息
    db_message = message.create(db, obj_in=message_in, conversation_id=conversation_id)

    # 更新会话消息计数和最后消息时间
    db_conversation.message_count += 1
    db_conversation.last_message_at = datetime.utcnow()
    db_conversation.updated_at = datetime.utcnow()
    db.add(db_conversation)
    db.commit()

    # 更新用户消息限制
    if daily_limit:
        user_conversation_limit.update_current_value(
            db, db_obj=daily_limit, increment=1
        )

    return MessagePublic.from_orm(db_message)


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
async def get_messages(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(50, ge=1, le=200, description="返回的记录数"),
    sender_type: Optional[str] = Query(None, description="发送者类型过滤"),
    content_type: Optional[str] = Query(None, description="内容类型过滤"),
    since: Optional[datetime] = Query(None, description="开始时间"),
    until: Optional[datetime] = Query(None, description="结束时间"),
) -> MessageListResponse:
    """获取消息列表"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 转换类型参数
    sender_type_enum = None
    if sender_type:
        try:
            sender_type_enum = SenderType(sender_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的发送者类型: {sender_type}",
            )

    content_type_enum = None
    if content_type:
        try:
            content_type_enum = ContentType(content_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的内容类型: {content_type}",
            )

    messages, total = message.get_multi(
        db,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit,
        sender_type=sender_type_enum,
        content_type=content_type_enum,
        since=since,
        until=until,
    )

    return MessageListResponse(
        messages=[MessagePublic.from_orm(msg) for msg in messages],
        total=total,
        skip=skip,
        limit=limit,
    )
