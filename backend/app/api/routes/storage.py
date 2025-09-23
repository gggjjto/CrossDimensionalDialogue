"""
存储相关API路由

提供文件上传、下载、删除等存储相关接口
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from app.api.deps import get_current_active_user
from app.models.user import User
from app.services.qiniu_storage_service import qiniu_storage_service
from app.utils.qiniu_storage import QiniuStorageError

router = APIRouter()


@router.post("/upload/audio")
async def upload_audio_file(
    file: UploadFile = File(...),
    conversation_id: Optional[int] = Form(None),
    current_user: User = Depends(get_current_active_user),
):
    """
    上传音频文件

    Args:
        file: 音频文件
        conversation_id: 对话ID（可选）
        current_user: 当前用户

    Returns:
        JSONResponse: 上传结果
    """
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只支持音频文件"
            )

        # 保存临时文件
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file.filename.split('.')[-1]}"
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # 上传到七牛云
            result = qiniu_storage_service.upload_audio_file(
                file_path=tmp_file_path,
                user_id=current_user.id,
                conversation_id=conversation_id,
                file_type="audio",
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "音频文件上传成功",
                    "data": {
                        "key": result["key"],
                        "url": result["url"],
                        "file_size": result["file_size"],
                        "original_name": result["original_name"],
                        "conversation_id": conversation_id,
                    },
                },
            )
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)

    except QiniuStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"上传失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}",
        )


@router.post("/upload/image")
async def upload_image_file(
    file: UploadFile = File(...),
    category: str = Form("general"),
    current_user: User = Depends(get_current_active_user),
):
    """
    上传图片文件

    Args:
        file: 图片文件
        category: 图片分类
        current_user: 当前用户

    Returns:
        JSONResponse: 上传结果
    """
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只支持图片文件"
            )

        # 保存临时文件
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=f".{file.filename.split('.')[-1]}"
        ) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        try:
            # 上传到七牛云
            result = qiniu_storage_service.upload_image_file(
                file_path=tmp_file_path,
                user_id=current_user.id,
                category=category,
                file_type="image",
            )

            # 生成缩略图URL
            thumbnail_url = qiniu_storage_service.get_image_thumbnail_url(
                key=result["key"], width=200, height=200
            )

            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content={
                    "message": "图片文件上传成功",
                    "data": {
                        "key": result["key"],
                        "url": result["url"],
                        "thumbnail_url": thumbnail_url,
                        "file_size": result["file_size"],
                        "original_name": result["original_name"],
                        "category": category,
                    },
                },
            )
        finally:
            # 清理临时文件
            os.unlink(tmp_file_path)

    except QiniuStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"上传失败: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"服务器错误: {str(e)}",
        )


@router.get("/files/{file_key}")
async def get_file_url(
    file_key: str,
    private: bool = False,
    expires: int = 3600,
    current_user: User = Depends(get_current_active_user),
):
    """
    获取文件访问URL

    Args:
        file_key: 文件key
        private: 是否使用私有URL
        expires: 私有URL过期时间（秒）
        current_user: 当前用户

    Returns:
        JSONResponse: 文件URL信息
    """
    try:
        url = qiniu_storage_service.get_file_url(
            key=file_key, private=private, expires=expires
        )

        return JSONResponse(
            content={
                "file_key": file_key,
                "url": url,
                "private": private,
                "expires": expires if private else None,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取文件URL失败: {str(e)}",
        )


@router.delete("/files/{file_key}")
async def delete_file(
    file_key: str, current_user: User = Depends(get_current_active_user)
):
    """
    删除文件

    Args:
        file_key: 文件key
        current_user: 当前用户

    Returns:
        JSONResponse: 删除结果
    """
    try:
        from app.utils.qiniu_storage import qiniu_client

        success = qiniu_client.delete_file(file_key)

        if success:
            return JSONResponse(
                content={"message": "文件删除成功", "file_key": file_key}
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件删除失败"
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文件失败: {str(e)}",
        )


@router.delete("/files/batch")
async def delete_files_batch(
    file_keys: List[str], current_user: User = Depends(get_current_active_user)
):
    """
    批量删除文件

    Args:
        file_keys: 文件key列表
        current_user: 当前用户

    Returns:
        JSONResponse: 删除结果
    """
    try:
        from app.utils.qiniu_storage import qiniu_client

        result = qiniu_client.delete_files(file_keys)

        return JSONResponse(
            content={
                "message": "批量删除完成",
                "success": result["success"],
                "deleted_count": len(file_keys),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除失败: {str(e)}",
        )


@router.get("/stats")
async def get_storage_stats(current_user: User = Depends(get_current_active_user)):
    """
    获取用户存储统计

    Args:
        current_user: 当前用户

    Returns:
        JSONResponse: 存储统计信息
    """
    try:
        stats = qiniu_storage_service.get_storage_stats(user_id=current_user.id)

        return JSONResponse(
            content={
                "user_id": current_user.id,
                "total_files": stats["total_files"],
                "total_size": stats["total_size"],
                "total_size_mb": stats["total_size_mb"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取存储统计失败: {str(e)}",
        )


@router.get("/images/{file_key}/thumbnail")
async def get_image_thumbnail(
    file_key: str,
    width: int = 200,
    height: int = 200,
    quality: int = 80,
    current_user: User = Depends(get_current_active_user),
):
    """
    获取图片缩略图URL

    Args:
        file_key: 图片文件key
        width: 宽度
        height: 高度
        quality: 质量（1-100）
        current_user: 当前用户

    Returns:
        JSONResponse: 缩略图URL
    """
    try:
        thumbnail_url = qiniu_storage_service.get_image_thumbnail_url(
            key=file_key, width=width, height=height, quality=quality
        )

        return JSONResponse(
            content={
                "file_key": file_key,
                "thumbnail_url": thumbnail_url,
                "width": width,
                "height": height,
                "quality": quality,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取缩略图失败: {str(e)}",
        )
