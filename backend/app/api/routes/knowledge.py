"""
知识库管理API路由
"""

import uuid
import logging
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.knowledge import (
    KnowledgeBase,
    KnowledgeItem,
    KnowledgeBaseCreate,
    KnowledgeItemCreate,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeType,
    KnowledgeSource,
)
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/knowledge-bases",
    status_code=status.HTTP_201_CREATED,
    summary="创建知识库",
    description="创建一个新的知识库",
)
async def create_knowledge_base(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_base: KnowledgeBaseCreate = Body(...),
) -> Dict[str, Any]:
    """
    创建知识库
    """
    try:
        # 创建知识库
        db_knowledge_base = KnowledgeBase(
            name=knowledge_base.name,
            description=knowledge_base.description,
            character_id=knowledge_base.character_id,
            knowledge_type=knowledge_base.knowledge_type,
            source=knowledge_base.source,
        )

        db.add(db_knowledge_base)
        db.commit()
        db.refresh(db_knowledge_base)

        return {
            "success": True,
            "message": "知识库创建成功",
            "knowledge_base": {
                "id": db_knowledge_base.id,
                "name": db_knowledge_base.name,
                "description": db_knowledge_base.description,
                "character_id": db_knowledge_base.character_id,
                "knowledge_type": db_knowledge_base.knowledge_type,
                "source": db_knowledge_base.source,
                "is_active": db_knowledge_base.is_active,
                "created_at": db_knowledge_base.created_at,
            },
        }

    except Exception as e:
        logger.error(f"创建知识库失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="创建知识库失败"
        )


@router.get(
    "/knowledge-bases",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="获取知识库列表",
    description="获取所有知识库列表",
)
async def get_knowledge_bases(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    character_id: Optional[uuid.UUID] = None,
    knowledge_type: Optional[KnowledgeType] = None,
) -> List[Dict[str, Any]]:
    """
    获取知识库列表
    """
    try:
        from sqlmodel import select

        query = select(KnowledgeBase).where(KnowledgeBase.is_active == True)

        if character_id:
            query = query.where(KnowledgeBase.character_id == character_id)

        if knowledge_type:
            query = query.where(KnowledgeBase.knowledge_type == knowledge_type)

        knowledge_bases = db.exec(query).all()

        result = []
        for kb in knowledge_bases:
            result.append(
                {
                    "id": kb.id,
                    "name": kb.name,
                    "description": kb.description,
                    "character_id": kb.character_id,
                    "knowledge_type": kb.knowledge_type,
                    "source": kb.source,
                    "is_active": kb.is_active,
                    "created_at": kb.created_at,
                    "updated_at": kb.updated_at,
                }
            )

        return result

    except Exception as e:
        logger.error(f"获取知识库列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识库列表失败",
        )


@router.post(
    "/knowledge-bases/{knowledge_base_id}/items",
    status_code=status.HTTP_201_CREATED,
    summary="添加知识条目",
    description="向知识库中添加新的知识条目",
)
async def add_knowledge_item(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_base_id: uuid.UUID,
    knowledge_item: KnowledgeItemCreate = Body(...),
) -> Dict[str, Any]:
    """
    添加知识条目
    """
    try:
        # 检查知识库是否存在
        knowledge_base = db.get(KnowledgeBase, knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )

        # 添加知识条目
        db_knowledge_item = await rag_service.add_knowledge_item(
            db=db,
            knowledge_base_id=knowledge_base_id,
            title=knowledge_item.title,
            content=knowledge_item.content,
            summary=knowledge_item.summary,
            tags=knowledge_item.tags,
            metadata=knowledge_item.metadata,
        )

        return {
            "success": True,
            "message": "知识条目添加成功",
            "knowledge_item": {
                "id": db_knowledge_item.id,
                "knowledge_base_id": db_knowledge_item.knowledge_base_id,
                "title": db_knowledge_item.title,
                "content": db_knowledge_item.content,
                "summary": db_knowledge_item.summary,
                "tags": db_knowledge_item.tags,
                "metadata": db_knowledge_item.metadata,
                "access_count": db_knowledge_item.access_count,
                "is_active": db_knowledge_item.is_active,
                "created_at": db_knowledge_item.created_at,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加知识条目失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="添加知识条目失败"
        )


@router.post(
    "/knowledge/search",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="搜索知识",
    description="在知识库中搜索相关知识",
)
async def search_knowledge(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    search_request: KnowledgeSearchRequest = Body(...),
) -> List[Dict[str, Any]]:
    """
    搜索知识
    """
    try:
        # 执行知识搜索
        results = await rag_service.search_knowledge(db, search_request)

        # 构建响应数据
        result = []
        for search_result in results:
            result.append(
                {
                    "knowledge_item": {
                        "id": search_result.knowledge_item.id,
                        "title": search_result.knowledge_item.title,
                        "content": search_result.knowledge_item.content,
                        "summary": search_result.knowledge_item.summary,
                        "tags": search_result.knowledge_item.tags,
                        "metadata": search_result.knowledge_item.metadata,
                    },
                    "relevance_score": search_result.relevance_score,
                    "matched_content": search_result.matched_content,
                    "context": search_result.context,
                }
            )

        return result

    except Exception as e:
        logger.error(f"搜索知识失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="搜索知识失败"
        )


@router.get(
    "/knowledge-bases/{knowledge_base_id}/items",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="获取知识条目列表",
    description="获取指定知识库中的所有知识条目",
)
async def get_knowledge_items(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_base_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    获取知识条目列表
    """
    try:
        from sqlmodel import select

        # 检查知识库是否存在
        knowledge_base = db.get(KnowledgeBase, knowledge_base_id)
        if not knowledge_base:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识库不存在"
            )

        # 获取知识条目
        query = (
            select(KnowledgeItem)
            .where(KnowledgeItem.knowledge_base_id == knowledge_base_id)
            .where(KnowledgeItem.is_active == True)
            .order_by(KnowledgeItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        knowledge_items = db.exec(query).all()

        result = []
        for item in knowledge_items:
            result.append(
                {
                    "id": item.id,
                    "knowledge_base_id": item.knowledge_base_id,
                    "title": item.title,
                    "content": item.content,
                    "summary": item.summary,
                    "tags": item.tags,
                    "metadata": item.metadata,
                    "access_count": item.access_count,
                    "is_active": item.is_active,
                    "created_at": item.created_at,
                    "updated_at": item.updated_at,
                }
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取知识条目列表失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="获取知识条目列表失败",
        )


@router.put(
    "/knowledge-items/{knowledge_item_id}/embedding",
    status_code=status.HTTP_200_OK,
    summary="更新知识条目嵌入向量",
    description="重新生成知识条目的嵌入向量",
)
async def update_knowledge_item_embedding(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    knowledge_item_id: uuid.UUID,
) -> Dict[str, Any]:
    """
    更新知识条目嵌入向量
    """
    try:
        # 更新嵌入向量
        success = await rag_service.update_knowledge_item_embedding(
            db, knowledge_item_id
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="知识条目不存在"
            )

        return {"success": True, "message": "嵌入向量更新成功"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新嵌入向量失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="更新嵌入向量失败"
        )
