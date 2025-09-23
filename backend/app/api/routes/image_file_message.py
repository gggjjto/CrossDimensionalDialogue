"""
图片和文件消息API路由
"""

import uuid
import logging
from typing import List, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
    Query,
)
from fastapi.responses import StreamingResponse
from sqlmodel import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.image_file_message import (
    ImageMessageCreate,
    ImageMessagePublic,
    ImageMessageListResponse,
    ImageMessageUpdate,
    FileMessageCreate,
    FileMessagePublic,
    FileMessageListResponse,
    FileMessageUpdate,
    FileProcessingTaskPublic,
    FileProcessingTaskListResponse,
    ImageUploadRequest,
    FileUploadRequest,
    ImageProcessRequest,
    ProcessingStatus,
    SecurityScanStatus,
    TaskType,
)
from app.crud.image_file_message import (
    image_message,
    file_message,
    file_processing_task,
)
from app.services.image_processing_service import image_processing_service
from app.services.file_processing_service import file_processing_service
from app.services.storage_service import storage_service
from app.utils.response import success_response, error_response

logger = logging.getLogger(__name__)

router = APIRouter()


# 图片消息API
@router.post(
    "/images/upload",
    response_model=ImageMessagePublic,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    conversation_id: Optional[uuid.UUID] = Form(None),
    compress: bool = Form(True),
    max_width: int = Form(1920),
    max_height: int = Form(1080),
    quality: int = Form(85),
) -> ImageMessagePublic:
    """上传图片"""
    try:
        # 验证文件类型
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="只支持图片文件"
            )

        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="图片文件大小不能超过10MB",
            )

        # 处理图片
        processed_image = await image_processing_service.process_image(
            file_content=file_content,
            file_name=file.filename,
            compress=compress,
            max_width=max_width,
            max_height=max_height,
            quality=quality,
        )

        # 上传到存储
        file_url = await storage_service.upload_file(
            file_data=processed_image["compressed_data"],
            file_name=processed_image["file_name"],
            folder="images",
        )

        thumbnail_url = None
        if processed_image.get("thumbnail_data"):
            thumbnail_url = await storage_service.upload_file(
                file_data=processed_image["thumbnail_data"],
                file_name=f"thumb_{processed_image['file_name']}",
                folder="thumbnails",
            )

        # 创建图片消息记录
        image_data = ImageMessageCreate(
            message_id=uuid.uuid4(),  # 临时ID，实际使用时需要关联真实消息
            file_url=file_url,
            file_name=processed_image["file_name"],
            file_size=len(processed_image["compressed_data"]),
            mime_type=processed_image["mime_type"],
            width=processed_image["width"],
            height=processed_image["height"],
            format=processed_image["format"],
            quality_score=processed_image.get("quality_score"),
            thumbnail_url=thumbnail_url,
            compressed_url=file_url,
            metadata=processed_image.get("metadata"),
            processing_status=ProcessingStatus.COMPLETED,
        )

        db_image = image_message.create(db, obj_in=image_data)
        return ImageMessagePublic.from_orm(db_image)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"图片上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"图片上传失败: {str(e)}",
        )


@router.get("/images/{image_id}", response_model=ImageMessagePublic)
async def get_image(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_id: uuid.UUID,
) -> ImageMessagePublic:
    """获取图片详情"""
    db_image = image_message.get(db, id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    return ImageMessagePublic.from_orm(db_image)


@router.get("/images/", response_model=ImageMessageListResponse)
async def get_images(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    conversation_id: Optional[uuid.UUID] = Query(None, description="会话ID过滤"),
    format: Optional[str] = Query(None, description="图片格式过滤"),
    status: Optional[ProcessingStatus] = Query(None, description="处理状态过滤"),
    order_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
) -> ImageMessageListResponse:
    """获取图片列表"""
    images, total = image_message.get_multi(
        db,
        skip=skip,
        limit=limit,
        conversation_id=conversation_id,
        format=format,
        status=status,
        order_by=order_by,
        order=order,
    )

    return ImageMessageListResponse(
        images=[ImageMessagePublic.from_orm(img) for img in images],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.put("/images/{image_id}", response_model=ImageMessagePublic)
async def update_image(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_id: uuid.UUID,
    image_update: ImageMessageUpdate,
) -> ImageMessagePublic:
    """更新图片信息"""
    db_image = image_message.get(db, id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    updated_image = image_message.update(db, db_obj=db_image, obj_in=image_update)
    return ImageMessagePublic.from_orm(updated_image)


@router.delete("/images/{image_id}")
async def delete_image(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_id: uuid.UUID,
):
    """删除图片"""
    db_image = image_message.get(db, id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    # 删除存储文件
    try:
        await storage_service.delete_file(db_image.file_url)
        if db_image.thumbnail_url:
            await storage_service.delete_file(db_image.thumbnail_url)
        if db_image.compressed_url and db_image.compressed_url != db_image.file_url:
            await storage_service.delete_file(db_image.compressed_url)
    except Exception as e:
        logger.warning(f"删除存储文件失败: {str(e)}")

    # 删除数据库记录
    image_message.delete(db, id=image_id)

    return success_response("图片删除成功")


@router.post("/images/{image_id}/process")
async def process_image(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    image_id: uuid.UUID,
    process_request: ImageProcessRequest,
):
    """处理图片"""
    db_image = image_message.get(db, id=image_id)
    if not db_image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="图片不存在")

    # 创建处理任务
    task_data = FileProcessingTaskCreate(
        image_message_id=image_id,
        task_type=TaskType.IMAGE_FORMAT_CONVERT,
        status=ProcessingStatus.PENDING,
    )

    task = file_processing_task.create(db, obj_in=task_data)

    # 异步处理图片
    # 这里应该启动后台任务处理图片

    return success_response("图片处理任务已创建", data={"task_id": task.id})


# 文件消息API
@router.post(
    "/files/upload",
    response_model=FileMessagePublic,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file: UploadFile = File(...),
    conversation_id: Optional[uuid.UUID] = Form(None),
    scan_security: bool = Form(True),
) -> FileMessagePublic:
    """上传文件"""
    try:
        # 验证文件大小
        file_content = await file.read()
        if len(file_content) > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="文件大小不能超过100MB"
            )

        # 处理文件
        processed_file = await file_processing_service.process_file(
            file_content=file_content,
            file_name=file.filename,
            scan_security=scan_security,
        )

        # 上传到存储
        file_url = await storage_service.upload_file(
            file_data=file_content,
            file_name=processed_file["file_name"],
            folder="files",
        )

        preview_url = None
        if processed_file.get("preview_data"):
            preview_url = await storage_service.upload_file(
                file_data=processed_file["preview_data"],
                file_name=f"preview_{processed_file['file_name']}",
                folder="previews",
            )

        # 创建文件消息记录
        file_data = FileMessageCreate(
            message_id=uuid.uuid4(),  # 临时ID，实际使用时需要关联真实消息
            file_url=file_url,
            file_name=processed_file["file_name"],
            file_size=len(file_content),
            mime_type=processed_file["mime_type"],
            file_extension=processed_file["file_extension"],
            file_type=processed_file["file_type"],
            checksum=processed_file.get("checksum"),
            metadata=processed_file.get("metadata"),
            preview_url=preview_url,
            processing_status=ProcessingStatus.COMPLETED,
            security_scan_status=processed_file.get(
                "security_status", SecurityScanStatus.SAFE
            ),
        )

        db_file = file_message.create(db, obj_in=file_data)
        return FileMessagePublic.from_orm(db_file)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}",
        )


@router.get("/files/{file_id}", response_model=FileMessagePublic)
async def get_file(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file_id: uuid.UUID,
) -> FileMessagePublic:
    """获取文件详情"""
    db_file = file_message.get(db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    return FileMessagePublic.from_orm(db_file)


@router.get("/files/", response_model=FileMessageListResponse)
async def get_files(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    conversation_id: Optional[uuid.UUID] = Query(None, description="会话ID过滤"),
    file_type: Optional[str] = Query(None, description="文件类型过滤"),
    status: Optional[ProcessingStatus] = Query(None, description="处理状态过滤"),
    security_status: Optional[SecurityScanStatus] = Query(
        None, description="安全状态过滤"
    ),
    order_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
) -> FileMessageListResponse:
    """获取文件列表"""
    files, total = file_message.get_multi(
        db,
        skip=skip,
        limit=limit,
        conversation_id=conversation_id,
        file_type=file_type,
        status=status,
        security_status=security_status,
        order_by=order_by,
        order=order,
    )

    return FileMessageListResponse(
        files=[FileMessagePublic.from_orm(f) for f in files],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/files/{file_id}/download")
async def download_file(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file_id: uuid.UUID,
):
    """下载文件"""
    db_file = file_message.get(db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 检查安全状态
    if db_file.security_scan_status == SecurityScanStatus.UNSAFE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="文件未通过安全扫描，无法下载"
        )

    # 增加下载次数
    file_message.increment_download_count(db, db_obj=db_file)

    # 获取文件流
    try:
        file_stream = await storage_service.get_file_stream(db_file.file_url)

        return StreamingResponse(
            file_stream,
            media_type=db_file.mime_type,
            headers={
                "Content-Disposition": f"attachment; filename={db_file.file_name}",
                "Content-Length": str(db_file.file_size),
            },
        )
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="文件下载失败"
        )


@router.get("/files/{file_id}/preview")
async def preview_file(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file_id: uuid.UUID,
):
    """文件预览"""
    db_file = file_message.get(db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    if not db_file.preview_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="文件预览不存在"
        )

    try:
        preview_stream = await storage_service.get_file_stream(db_file.preview_url)

        return StreamingResponse(
            preview_stream,
            media_type="image/jpeg",  # 预览通常是图片
        )
    except Exception as e:
        logger.error(f"文件预览失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="文件预览失败"
        )


@router.delete("/files/{file_id}")
async def delete_file(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    file_id: uuid.UUID,
):
    """删除文件"""
    db_file = file_message.get(db, id=file_id)
    if not db_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")

    # 删除存储文件
    try:
        await storage_service.delete_file(db_file.file_url)
        if db_file.preview_url:
            await storage_service.delete_file(db_file.preview_url)
    except Exception as e:
        logger.warning(f"删除存储文件失败: {str(e)}")

    # 删除数据库记录
    file_message.delete(db, id=file_id)

    return success_response("文件删除成功")


# 处理任务API
@router.get("/tasks/", response_model=FileProcessingTaskListResponse)
async def get_processing_tasks(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    file_message_id: Optional[uuid.UUID] = Query(None, description="文件消息ID过滤"),
    image_message_id: Optional[uuid.UUID] = Query(None, description="图片消息ID过滤"),
    task_type: Optional[TaskType] = Query(None, description="任务类型过滤"),
    status: Optional[ProcessingStatus] = Query(None, description="任务状态过滤"),
    order_by: str = Query("created_at", description="排序字段"),
    order: str = Query("desc", description="排序方向"),
) -> FileProcessingTaskListResponse:
    """获取处理任务列表"""
    tasks, total = file_processing_task.get_multi(
        db,
        skip=skip,
        limit=limit,
        file_message_id=file_message_id,
        image_message_id=image_message_id,
        task_type=task_type,
        status=status,
        order_by=order_by,
        order=order,
    )

    return FileProcessingTaskListResponse(
        tasks=[FileProcessingTaskPublic.from_orm(task) for task in tasks],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/tasks/{task_id}", response_model=FileProcessingTaskPublic)
async def get_processing_task(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    task_id: uuid.UUID,
) -> FileProcessingTaskPublic:
    """获取处理任务详情"""
    db_task = file_processing_task.get(db, id=task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="处理任务不存在"
        )

    return FileProcessingTaskPublic.from_orm(db_task)
