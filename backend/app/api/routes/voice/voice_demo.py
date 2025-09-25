"""
音色示例语音生成API路由
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.api.deps import get_db, get_current_active_superuser, get_current_user
from app.models.user import User
from app.services.voice_demo_service import voice_demo_service
from app.utils.response import success_response

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice-demo", tags=["voice-demo"])


@router.post("/generate-all")
async def generate_all_voice_demos(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    provider: str = Query("qwen3-tts", description="音色提供方"),
    force_regenerate: bool = Query(False, description="是否强制重新生成"),
):
    """
    为所有音色生成示例语音

    需要超级用户权限
    """
    try:
        result = await voice_demo_service.generate_demo_audio_for_all_voices(
            session=db, provider=provider, force_regenerate=force_regenerate
        )

        if result["success"]:
            return success_response(
                data=result,
                msg=f"音色示例语音生成完成: 成功 {result['success_count']}, 失败 {result['failed_count']}, 跳过 {result['skipped_count']}",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "生成失败"),
            )

    except Exception as e:
        logger.error(f"生成音色示例语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成音色示例语音失败: {str(e)}",
        )


@router.post("/generate/{voice_id}")
async def generate_voice_demo(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
    voice_id: str,
    demo_text: Optional[str] = Query(None, description="自定义示例文本"),
):
    """
    为指定音色生成示例语音

    需要超级用户权限
    """
    try:
        from app.crud.voice_catalog import voice_catalog_crud

        # 获取音色信息
        voice_catalog = voice_catalog_crud.get(db, id=voice_id)
        if not voice_catalog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="音色未找到"
            )

        # 生成示例语音
        audio_url = await voice_demo_service.generate_demo_audio_for_voice(
            session=db, voice_catalog=voice_catalog, demo_text=demo_text
        )

        if audio_url:
            return success_response(
                data={
                    "voice_id": voice_id,
                    "voice_name": voice_catalog.name,
                    "voice": voice_catalog.voice,
                    "preview_url": audio_url,
                },
                msg="音色示例语音生成成功",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="生成音色示例语音失败",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"生成音色示例语音失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"生成音色示例语音失败: {str(e)}",
        )


@router.get("/status")
async def get_voice_demo_status(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    provider: str = Query("qwen3-tts", description="音色提供方"),
):
    """
    获取音色示例语音生成状态

    需要登录权限
    """
    try:
        from app.crud.voice_catalog import voice_catalog_crud

        # 获取所有音色
        voices, total = voice_catalog_crud.get_multi(db, provider=provider, limit=500)

        # 统计状态
        with_demo = sum(1 for voice in voices if voice.preview_url)
        without_demo = total - with_demo

        return success_response(
            data={
                "total": total,
                "with_demo": with_demo,
                "without_demo": without_demo,
                "completion_rate": (
                    round(with_demo / total * 100, 2) if total > 0 else 0
                ),
                "voices": [
                    {
                        "id": str(voice.id),
                        "name": voice.name,
                        "voice": voice.voice,
                        "has_demo": bool(voice.preview_url),
                        "preview_url": voice.preview_url,
                    }
                    for voice in voices
                ],
            },
            msg="获取音色示例语音状态成功",
        )

    except Exception as e:
        logger.error(f"获取音色示例语音状态失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取音色示例语音状态失败: {str(e)}",
        )
