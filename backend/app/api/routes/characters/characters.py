import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from app.api.deps import get_db, get_current_active_superuser, get_current_user
from app.crud.character import character, character_tag
from app.crud.character_embedding import character_embedding_crud
from app.services.embedding_service import embedding_service
from app.services.character_image_service import character_image_service
from app.services.qiniu_storage_service import QiniuStorageService
from app.models.character import (
    CharacterCreate,
    CharacterUpdate,
    CharacterTagCreate,
    CharacterTagUpdate,
    CharacterSearchRequest,
)
from app.models.user import User
from app.utils.response import success_response
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_character(
    *,
    db: Session = Depends(get_db),
    character_in: CharacterCreate,
    current_user: User = Depends(get_current_user),
):
    """
    创建新角色。

    需要用户权限。
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

    # 生成向量嵌入
    try:
        await embedding_service.generate_character_embeddings(character_obj, db)
    except Exception as e:
        # 记录错误但不影响角色创建
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(f"生成角色向量嵌入失败: {str(e)}")

    # 如果启用AI图片生成且没有提供头像URL，则生成AI形象图片
    if character_obj.auto_generate_image and not character_obj.avatar_url:
        try:
            ai_image_bytes = await character_image_service.generate_character_image(
                character_obj,
                style=character_obj.image_style or "realistic",
                size=character_obj.image_size or "720*1280",
            )
            if ai_image_bytes:
                # 上传图片到存储服务
                storage_service = QiniuStorageService()
                upload_result = storage_service.upload_character_avatar_bytes(
                    ai_image_bytes, character_obj.id
                )

                # 更新角色的头像URL
                character_obj.avatar_url = upload_result["url"]
                db.commit()
                db.refresh(character_obj)
        except Exception as e:
            logger.warning(f"生成角色AI形象图片失败: {str(e)}")

    return success_response(data=character_obj.model_dump(), msg="角色创建成功")


@router.get("/search")
async def search_characters(
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

    if search_type == "text":
        result = character_embedding_crud.text_search_characters(db, search_request)
    elif search_type == "vector":
        # 生成查询向量
        query_embedding = await embedding_service.generate_embedding(query)
        result = character_embedding_crud.vector_search_characters(
            db, search_request, query_embedding
        )
    elif search_type == "hybrid":
        # 生成查询向量
        query_embedding = await embedding_service.generate_embedding(query)
        result = character_embedding_crud.hybrid_search_characters(
            db, search_request, query_embedding
        )
    else:
        raise HTTPException(status_code=400, detail="不支持的搜索类型")

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

    try:
        tag_obj = character_tag.delete(db, id=tag_id)
        return success_response(data=tag_obj.model_dump(), msg="标签删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# AI图片生成相关路由
@router.post("/{character_id}/generate-image")
async def generate_character_image(
    *,
    db: Session = Depends(get_db),
    character_id: uuid.UUID,
    style: str = Query(
        "realistic", description="图片风格: realistic, anime, cartoon, artistic"
    ),
    size: str = Query("720*1280", description="图片尺寸: 720*1280"),
    current_user: User = Depends(get_current_user),
):
    """
    为角色生成AI形象图片。

    需要用户权限。
    """
    character_obj = character.get(db, id=character_id)
    if not character_obj:
        raise HTTPException(status_code=404, detail="角色未找到")

    try:
        ai_image_bytes = await character_image_service.generate_character_image(
            character_obj, style=style, size=size
        )

        if ai_image_bytes:
            # 上传图片到存储服务
            storage_service = QiniuStorageService()
            upload_result = storage_service.upload_character_avatar_bytes(
                ai_image_bytes, character_obj.id
            )

            # 更新角色的头像URL
            character_obj.avatar_url = upload_result["url"]
            db.commit()
            db.refresh(character_obj)

            return success_response(
                data={
                    "character_id": str(character_id),
                    "avatar_url": upload_result["url"],
                    "style": style,
                    "size": size,
                },
                msg="AI形象图片生成成功",
            )
        else:
            raise HTTPException(status_code=500, detail="AI形象图片生成失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成AI形象图片失败: {str(e)}")


@router.get("/image-generation/styles", include_in_schema=False)
def get_image_generation_styles():
    """
    获取支持的AI图片生成风格。
    """
    styles = character_image_service.get_supported_styles()
    return success_response(data=styles, msg="获取图片风格成功")


@router.get("/image-generation/sizes", include_in_schema=False)
def get_image_generation_sizes():
    """
    获取支持的AI图片生成尺寸。
    """
    sizes = character_image_service.get_supported_sizes()
    return success_response(data=sizes, msg="获取图片尺寸成功")


@router.post("/{character_id}/validate-image", include_in_schema=False)
async def validate_character_image(
    *,
    db: Session = Depends(get_db),
    character_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
):
    """
    验证角色头像图片是否有效。

    需要用户权限。
    """
    character_obj = character.get(db, id=character_id)
    if not character_obj:
        raise HTTPException(status_code=404, detail="角色未找到")

    if not character_obj.avatar_url:
        raise HTTPException(status_code=400, detail="角色没有头像图片")

    try:
        is_valid = await character_image_service.validate_image_url(
            character_obj.avatar_url
        )

        return success_response(
            data={
                "character_id": str(character_id),
                "avatar_url": character_obj.avatar_url,
                "is_valid": is_valid,
            },
            msg="图片验证完成",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证图片失败: {str(e)}")
