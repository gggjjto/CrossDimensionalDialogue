import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlmodel import Session

from app.api.deps import get_db, get_current_active_superuser
from app.crud.character import character, character_tag
from app.models.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterTagCreate,
    CharacterTagUpdate,
    CharacterSearchRequest,
)
from app.models.user import User
from app.utils.response import success_response, error_response, not_found_response

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_character(
    *,
    db: Session = Depends(get_db),
    character_in: CharacterCreate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    创建新角色。

    需要超级用户权限。
    """
    # 检查角色名称是否已存在
    existing_character = character.get_by_name(db, name=character_in.name)
    if existing_character:
        raise HTTPException(status_code=400, detail="角色名称已存在")

    # 验证标签ID是否存在
    if character_in.tag_ids:
        for tag_id in character_in.tag_ids:
            existing_tag = character_tag.get(db, id=tag_id)
            if not existing_tag:
                raise HTTPException(status_code=400, detail=f"标签ID {tag_id} 不存在")

    character_obj = character.create(db, obj_in=character_in)
    return success_response(data=character_obj.model_dump(), msg="角色创建成功")


@router.get("/search")
def search_characters(
    *,
    db: Session = Depends(get_db),
    query: str = Query(..., description="搜索查询"),
    search_type: str = Query("text", description="搜索类型：text/vector/hybrid"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    tag_ids: Optional[List[uuid.UUID]] = Query(None, description="标签过滤"),
    is_active: Optional[bool] = Query(True, description="是否只搜索可用角色"),
):
    """
    搜索角色。

    支持文本搜索、向量搜索和混合搜索。
    """
    search_request = CharacterSearchRequest(
        query=query,
        search_type=search_type,
        limit=limit,
        offset=offset,
        tag_ids=tag_ids,
        is_active=is_active,
    )
    result = character.search(db, search_request=search_request)
    return success_response(data=result.model_dump(), msg="搜索完成")


@router.get("/")
def read_characters(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
    is_active: Optional[bool] = Query(None, description="是否只返回可用角色"),
    tag_ids: Optional[List[uuid.UUID]] = Query(None, description="标签ID过滤"),
):
    """
    获取角色列表。

    支持分页和过滤。
    """
    characters, total = character.get_multi(
        db, skip=skip, limit=limit, is_active=is_active, tag_ids=tag_ids
    )
    return success_response(
        data={
            "characters": [char.model_dump() for char in characters],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        msg="获取角色列表成功",
    )


@router.get("/{character_id}")
def read_character(
    *,
    db: Session = Depends(get_db),
    character_id: uuid.UUID,
):
    """
    根据ID获取角色详情。
    """
    character_obj = character.get(db, id=character_id)
    if not character_obj:
        raise HTTPException(status_code=404, detail="角色未找到")
    return success_response(data=character_obj.model_dump(), msg="获取角色详情成功")


@router.put("/{character_id}")
def update_character(
    *,
    db: Session = Depends(get_db),
    character_id: uuid.UUID,
    character_in: CharacterUpdate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    更新角色信息。

    需要超级用户权限。
    """
    character_obj = character.get(db, id=character_id)
    if not character_obj:
        raise HTTPException(status_code=404, detail="角色未找到")

    # 检查名称是否与其他角色冲突
    if character_in.name and character_in.name != character_obj.name:
        existing_character = character.get_by_name(db, name=character_in.name)
        if existing_character and existing_character.id != character_id:
            raise HTTPException(status_code=400, detail="角色名称已存在")

    # 验证标签ID是否存在
    if character_in.tag_ids is not None:
        for tag_id in character_in.tag_ids:
            existing_tag = character_tag.get(db, id=tag_id)
            if not existing_tag:
                raise HTTPException(status_code=400, detail=f"标签ID {tag_id} 不存在")

    character_obj = character.update(db, db_obj=character_obj, obj_in=character_in)
    return success_response(data=character_obj.model_dump(), msg="角色更新成功")


@router.delete("/{character_id}")
def delete_character(
    *,
    db: Session = Depends(get_db),
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    删除角色（软删除）。

    需要超级用户权限。
    """
    character_obj = character.get(db, id=character_id)
    if not character_obj:
        raise HTTPException(status_code=404, detail="角色未找到")

    character_obj = character.delete(db, id=character_id)
    return success_response(data=character_obj.model_dump(), msg="角色删除成功")


# 角色标签相关路由
@router.post("/tags/", status_code=status.HTTP_201_CREATED)
def create_character_tag(
    *,
    db: Session = Depends(get_db),
    tag_in: CharacterTagCreate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    创建新标签。

    需要超级用户权限。
    """
    # 检查标签名称是否已存在
    existing_tag = character_tag.get_by_name(db, name=tag_in.name)
    if existing_tag:
        raise HTTPException(status_code=400, detail="标签名称已存在")

    tag_obj = character_tag.create(db, obj_in=tag_in)
    return success_response(data=tag_obj.model_dump(), msg="标签创建成功")


@router.get("/tags/")
def read_character_tags(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回的记录数"),
):
    """
    获取标签列表。
    """
    tags, total = character_tag.get_multi(db, skip=skip, limit=limit)
    return success_response(
        data={
            "tags": [tag.model_dump() for tag in tags],
            "total": total,
            "skip": skip,
            "limit": limit,
        },
        msg="获取标签列表成功",
    )


@router.get("/tags/{tag_id}")
def read_character_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: uuid.UUID,
):
    """
    根据ID获取标签详情。
    """
    tag_obj = character_tag.get(db, id=tag_id)
    if not tag_obj:
        raise HTTPException(status_code=404, detail="标签未找到")
    return success_response(data=tag_obj.model_dump(), msg="获取标签详情成功")


@router.put("/tags/{tag_id}")
def update_character_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: uuid.UUID,
    tag_in: CharacterTagUpdate,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    更新标签信息。

    需要超级用户权限。
    """
    tag_obj = character_tag.get(db, id=tag_id)
    if not tag_obj:
        raise HTTPException(status_code=404, detail="标签未找到")

    # 检查名称是否与其他标签冲突
    if tag_in.name and tag_in.name != tag_obj.name:
        existing_tag = character_tag.get_by_name(db, name=tag_in.name)
        if existing_tag and existing_tag.id != tag_id:
            raise HTTPException(status_code=400, detail="标签名称已存在")

    tag_obj = character_tag.update(db, db_obj=tag_obj, obj_in=tag_in)
    return success_response(data=tag_obj.model_dump(), msg="标签更新成功")


@router.delete("/tags/{tag_id}")
def delete_character_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: uuid.UUID,
    current_user: User = Depends(get_current_active_superuser),
):
    """
    删除标签。

    需要超级用户权限。
    """
    tag_obj = character_tag.get(db, id=tag_id)
    if not tag_obj:
        raise HTTPException(status_code=404, detail="标签未找到")

    tag_obj = character_tag.delete(db, id=tag_id)
    return success_response(data=tag_obj.model_dump(), msg="标签删除成功")
