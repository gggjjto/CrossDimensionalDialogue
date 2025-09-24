import uuid
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from app.api.deps import get_db, get_current_user

# 配置日志
logger = logging.getLogger(__name__)
from app.crud.conversation import (
    conversation,
    message,
    conversation_context,
    conversation_tag,
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
    MessageUpdate,
    MessagePublic,
    MessageListResponse,
    MessageSearchRequest,
    MessageSearchResponse,
    ConversationStats,
    ConversationStatsResponse,
    ConversationExportRequest,
    ConversationExportResponse,
    SenderType,
    ContentType,
    MessageStatus,
)
from app.utils.response import success_response, error_response

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
    try:
        # 验证角色是否存在
        if conversation_in.character_id:
            from app.crud import character

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
        max_conversations_limit = user_conversation_limit.get_by_user_and_type(
            db, user_id=current_user.id, limit_type="max_conversations"
        )

        if (
            max_conversations_limit
            and user_conversation_count >= max_conversations_limit.limit_value
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"已达到最大会话数量限制: {max_conversations_limit.limit_value}",
            )

        # 创建会话
        db_conversation = conversation.create(
            db, obj_in=conversation_in, user_id=current_user.id
        )

        return ConversationPublic.from_orm(db_conversation)

    except HTTPException:
        # 重新抛出HTTP异常
        raise
    except IntegrityError as e:
        # 处理外键约束违反等数据库完整性错误
        logger.error(f"数据库完整性错误: {str(e)}")
        if "foreign key constraint" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关联数据不存在，请检查角色ID是否正确",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="数据验证失败"
            )
    except Exception as e:
        # 记录其他未预期的错误
        logger.error(f"创建对话时发生错误: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建对话时发生内部错误",
        )


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
    from app.models.conversation import ConversationStatus

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
        conv_dict["user"] = conv.user
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
        )

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在"
        )

    # 检查用户消息限制
    daily_limit = user_conversation_limit.get_by_user_and_type(
        db, user_id=current_user.id, limit_type="daily_messages"
    )

    if daily_limit:
        # 重置限制如果需要
        daily_limit = user_conversation_limit.reset_if_needed(
            db, db_obj=daily_limit
        )

        if daily_limit.current_value >= daily_limit.limit_value:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"已达到每日消息数量限制: {daily_limit.limit_value}",
            )

    # 设置发送者信息
    if message_in.sender_type == SenderType.USER:
        message_in.sender_id = current_user.id

    # 创建消息
    db_message = message.create(
        db, obj_in=message_in, conversation_id=conversation_id
    )

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


@router.get("/{conversation_id}/messages/{message_id}", response_model=MessagePublic)
async def get_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
) -> MessagePublic:
    """获取消息详情"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    db_message = message.get_by_conversation_and_id(
        db, id=message_id, conversation_id=conversation_id
    )

    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    return MessagePublic.from_orm(db_message)


@router.put("/{conversation_id}/messages/{message_id}", response_model=MessagePublic)
async def update_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
    message_in: MessageUpdate,
) -> MessagePublic:
    """更新消息"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    db_message = message.get_by_conversation_and_id(
        db, id=message_id, conversation_id=conversation_id
    )

    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 检查权限：只有消息发送者可以更新消息
    if (
        db_message.sender_type == SenderType.USER
        and db_message.sender_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限更新此消息"
        )

    # 更新消息
    db_message = message.update(db, db_obj=db_message, obj_in=message_in)

    return MessagePublic.from_orm(db_message)


@router.delete("/{conversation_id}/messages/{message_id}", response_model=MessagePublic)
async def delete_message(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    message_id: uuid.UUID,
) -> MessagePublic:
    """删除消息"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    db_message = message.get_by_conversation_and_id(
        db, id=message_id, conversation_id=conversation_id
    )

    if not db_message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")

    # 检查权限：只有消息发送者可以删除消息
    if (
        db_message.sender_type == SenderType.USER
        and db_message.sender_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="无权限删除此消息"
        )

    # 删除消息
    message.delete(db, id=message_id)

    # 更新会话消息计数
    db_conversation.message_count = max(0, db_conversation.message_count - 1)
    db_conversation.updated_at = datetime.utcnow()
    db.add(db_conversation)
    db.commit()

    return MessagePublic.from_orm(db_message)


@router.post("/{conversation_id}/messages/search", response_model=MessageSearchResponse)
async def search_messages(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    search_params: MessageSearchRequest,
) -> MessageSearchResponse:
    """搜索消息"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    messages, total = message.search(
        db, conversation_id=conversation_id, search_params=search_params
    )

    # 生成高亮显示（简单实现）
    highlight = {}
    if search_params.query:
        for msg in messages:
            if search_params.query.lower() in msg.content.lower():
                # 简单的关键词高亮
                highlighted_content = msg.content.replace(
                    search_params.query, f"<em>{search_params.query}</em>"
                )
                highlight[str(msg.id)] = highlighted_content

    return MessageSearchResponse(
        results=[MessagePublic.from_orm(msg) for msg in messages],
        total=total,
        query=search_params.query,
        highlight=highlight if highlight else None,
    )


# 统计和分析端点
@router.get("/{conversation_id}/stats", response_model=ConversationStatsResponse)
async def get_conversation_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
) -> ConversationStatsResponse:
    """获取会话统计"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 获取消息统计
    messages, _ = message.get_multi(
        db, conversation_id=conversation_id, skip=0, limit=10000
    )

    # 计算统计信息
    total_messages = len(messages)
    user_messages = len([m for m in messages if m.sender_type == SenderType.USER])
    character_messages = len(
        [m for m in messages if m.sender_type == SenderType.CHARACTER]
    )
    text_messages = len([m for m in messages if m.content_type == ContentType.TEXT])
    audio_messages = len([m for m in messages if m.content_type == ContentType.AUDIO])
    image_messages = len([m for m in messages if m.content_type == ContentType.IMAGE])

    total_duration = sum(m.audio_duration or 0 for m in messages)
    average_message_length = (
        sum(len(m.content) for m in messages) / total_messages
        if total_messages > 0
        else 0
    )

    # 简单的情感分析（这里只是示例，实际应该使用AI模型）
    positive_sentiment = 0.6  # 示例值
    neutral_sentiment = 0.3  # 示例值
    negative_sentiment = 0.1  # 示例值

    last_activity_at = max(m.created_at for m in messages) if messages else None

    stats = ConversationStats(
        total_messages=total_messages,
        user_messages=user_messages,
        character_messages=character_messages,
        text_messages=text_messages,
        audio_messages=audio_messages,
        image_messages=image_messages,
        total_duration=total_duration,
        average_message_length=average_message_length,
        positive_sentiment=positive_sentiment,
        neutral_sentiment=neutral_sentiment,
        negative_sentiment=negative_sentiment,
        last_activity_at=last_activity_at,
    )

    return ConversationStatsResponse(
        conversation_id=conversation_id,
        stats=stats,
        generated_at=datetime.utcnow(),
    )


@router.post("/{conversation_id}/export", response_model=ConversationExportResponse)
async def export_conversation(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    conversation_id: uuid.UUID,
    export_params: ConversationExportRequest,
) -> ConversationExportResponse:
    """导出会话数据"""
    # 检查会话是否存在且属于当前用户
    db_conversation = conversation.get_by_user_and_id(
        db, id=conversation_id, user_id=current_user.id
    )

    if not db_conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")

    # 这里应该实现实际的导出逻辑
    # 为了示例，我们返回一个模拟的响应
    download_url = (
        f"https://example.com/exports/{conversation_id}.{export_params.format}"
    )
    file_size = 1024000  # 示例文件大小
    expires_at = datetime.utcnow().replace(hour=23, minute=59, second=59)  # 当天结束

    return ConversationExportResponse(
        download_url=download_url,
        file_size=file_size,
        expires_at=expires_at,
    )
