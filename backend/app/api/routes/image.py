import mimetypes
import re
from datetime import datetime
from hashlib import md5

from app.api.deps import get_current_user
from app.models.user import User
from app.services.character_image_service import character_image_service
from app.services.qiniu_storage_service import QiniuStorageService
from app.utils.response import success_response
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

router = APIRouter(prefix="/image", tags=["image"])


@router.post("/generate")
async def generate_image(
    prompt: str,
    size: str = "720*1280",
    style: str = "realistic",
    quality: str = "standard",
    current_user: User = Depends(get_current_user),
):
    """
    使用AI生成图片
    """
    image_bytes = await character_image_service.generate_character_image_with_prompt(
        prompt, size, style, quality
    )

    # 上传到七牛云
    storage_service = QiniuStorageService()
    upload_result = storage_service.upload_character_avatar_bytes(
        image_bytes, current_user.id
    )

    return success_response(data=upload_result, msg="图片生成成功")


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    上传图片文件到对象存储（七牛）

    请求：multipart/form-data，字段名为 `file`
    响应：统一包装，返回至少 { url, key }
    """
    # 基础校验
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="未选择文件")

    content_type = file.content_type or mimetypes.guess_type(file.filename)[0] or ""
    if not content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="仅支持图片上传")

    # 读取数据
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="文件内容为空")

    # 生成存储 key
    # 目录：images/<user_id>/general/<YYYYMMDD>/<hash>_<safe_filename>
    today = datetime.now().strftime("%Y%m%d")
    filehash = md5(data).hexdigest()[:8]
    # 清理文件名中的不安全字符
    safe_name = re.sub(r"[^a-zA-Z0-9_.\-]", "_", file.filename)
    key = f"images/{current_user.id}/general/{today}/{filehash}_{safe_name}"

    # 确定最终的 content-type
    final_content_type = content_type or "image/png"

    # 执行上传
    storage_service = QiniuStorageService()
    result = storage_service.client.upload_data(
        data=data,
        key=key,
        content_type=final_content_type,
        overwrite=True,
    )

    # 返回统一响应（前端只需要 url，也可同时返回 key 等信息）
    return success_response(
        data={"url": result.get("url"), "key": result.get("key")}, msg="上传成功"
    )
