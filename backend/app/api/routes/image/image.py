from fastapi import APIRouter
from app.services.character_image_service import character_image_service
from app.services.qiniu_storage_service import QiniuStorageService
from app.models.user import User
from app.api.deps import get_current_user
from fastapi import Depends
from app.utils.response import success_response

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
    upload_result = storage_service.upload_character_avatar_bytes(image_bytes, current_user.id)

    return success_response(data=upload_result, msg="图片生成成功")
