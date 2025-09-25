"""
音色示例语音生成服务

为每个音色生成示例语音，上传到七牛云并更新数据库
"""

import asyncio
import logging
import tempfile
import os
from typing import List, Optional, Dict, Any
from sqlmodel import Session

from app.services.tts_service import TTSService, TTSRequest
from app.services.qiniu_storage_service import QiniuStorageService
from app.crud.voice_catalog import voice_catalog_crud
from app.models.voice_catalog import VoiceCatalog, VoiceCatalogUpdate

logger = logging.getLogger(__name__)


class VoiceDemoService:
    """音色示例语音生成服务"""

    def __init__(self):
        self.tts_service = TTSService()
        self.storage_service = QiniuStorageService()

    async def generate_demo_audio_for_voice(
        self,
        session: Session,
        voice_catalog: VoiceCatalog,
        demo_text: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
    ) -> Optional[str]:
        """
        为单个音色生成示例语音

        Args:
            session: 数据库会话
            voice_catalog: 音色目录对象
            demo_text: 示例文本，如果为None则使用默认文本
            max_retries: 最大重试次数
            retry_delay: 重试延迟时间（秒）

        Returns:
            音频URL或None
        """
        import asyncio

        for attempt in range(max_retries + 1):
            try:
                # 使用默认示例文本或自定义文本
                if not demo_text:
                    demo_text = self._get_default_demo_text(voice_catalog.name)

                # 创建TTS请求
                tts_request = TTSRequest(
                    text=demo_text,
                    voice=voice_catalog.voice,
                    audio_format="wav",
                    sample_rate=24000,
                )

                # 生成语音
                tts_response = await self.tts_service.synthesize(tts_request)

                if not tts_response.audio_bytes:
                    logger.error(
                        f"为音色 {voice_catalog.name} 生成语音失败：TTS返回空数据"
                    )
                    return None

                # 上传到七牛云
                audio_url = await self._upload_audio_to_storage(
                    tts_response.audio_bytes, voice_catalog.voice, voice_catalog.name
                )

                if audio_url:
                    # 更新数据库中的预览URL
                    update_data = VoiceCatalogUpdate(preview_url=audio_url)
                    voice_catalog_crud.update(
                        session, db_obj=voice_catalog, obj_in=update_data
                    )
                    logger.info(
                        f"为音色 {voice_catalog.name} 生成示例语音成功: {audio_url}"
                    )
                    return audio_url
                else:
                    logger.error(f"为音色 {voice_catalog.name} 上传音频失败")
                    return None

            except ValueError as e:
                error_msg = str(e)
                # 检查是否是限流错误
                if (
                    "Requests rate limit exceeded" in error_msg
                    or "Throttling" in error_msg
                ):
                    if attempt < max_retries:
                        wait_time = retry_delay * (2**attempt)  # 指数退避
                        logger.warning(
                            f"为音色 {voice_catalog.name} 遇到限流，第 {attempt + 1} 次重试，等待 {wait_time} 秒..."
                        )
                        await asyncio.sleep(wait_time)
                        continue
                    else:
                        logger.error(
                            f"为音色 {voice_catalog.name} 重试 {max_retries} 次后仍然限流"
                        )
                        return None
                else:
                    logger.error(
                        f"为音色 {voice_catalog.name} 生成示例语音失败: {error_msg}"
                    )
                    return None
            except Exception as e:
                logger.error(f"为音色 {voice_catalog.name} 生成示例语音失败: {str(e)}")
                return None

        return None

    async def generate_demo_audio_for_all_voices(
        self,
        session: Session,
        provider: str = "qwen3-tts",
        force_regenerate: bool = False,
    ) -> Dict[str, Any]:
        """
        为所有音色生成示例语音

        Args:
            session: 数据库会话
            provider: 音色提供方
            force_regenerate: 是否强制重新生成（即使已有预览URL）

        Returns:
            生成结果统计
        """
        try:
            # 获取所有音色
            voices, total = voice_catalog_crud.get_multi(
                session, provider=provider, limit=500
            )

            if not voices:
                logger.warning(f"没有找到 {provider} 的音色")
                return {"success": False, "message": "没有找到音色"}

            success_count = 0
            failed_count = 0
            skipped_count = 0
            results = []

            for i, voice in enumerate(voices):
                # 如果已有预览URL且不强制重新生成，则跳过
                if voice.preview_url and not force_regenerate:
                    skipped_count += 1
                    results.append(
                        {
                            "voice": voice.voice,
                            "name": voice.name,
                            "status": "skipped",
                            "url": voice.preview_url,
                        }
                    )
                    continue

                # 添加延迟以避免API限流
                if i > 0:  # 第一个请求不需要延迟
                    await asyncio.sleep(2)  # 每个请求间隔2秒

                # 生成示例语音
                audio_url = await self.generate_demo_audio_for_voice(session, voice)

                if audio_url:
                    success_count += 1
                    results.append(
                        {
                            "voice": voice.voice,
                            "name": voice.name,
                            "status": "success",
                            "url": audio_url,
                        }
                    )
                else:
                    failed_count += 1
                    results.append(
                        {
                            "voice": voice.voice,
                            "name": voice.name,
                            "status": "failed",
                            "url": None,
                        }
                    )

            logger.info(
                f"音色示例语音生成完成: 成功 {success_count}, 失败 {failed_count}, 跳过 {skipped_count}"
            )

            return {
                "success": True,
                "total": total,
                "success_count": success_count,
                "failed_count": failed_count,
                "skipped_count": skipped_count,
                "results": results,
            }

        except Exception as e:
            logger.error(f"批量生成音色示例语音失败: {str(e)}")
            return {"success": False, "message": str(e)}

    async def _upload_audio_to_storage(
        self, audio_bytes: bytes, voice: str, name: str
    ) -> Optional[str]:
        """
        上传音频到七牛云存储

        Args:
            audio_bytes: 音频字节数据
            voice: 音色标识
            name: 音色名称

        Returns:
            音频URL或None
        """
        try:
            # 创建临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_bytes)
                temp_file_path = temp_file.name

            try:
                # 生成文件key
                from datetime import datetime

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                key = f"voice_demos/{voice}/{timestamp}_{name}.wav"

                # 确定内容类型
                import mimetypes

                content_type = mimetypes.guess_type("demo.wav")[0] or "audio/wav"

                # 上传数据
                result = self.storage_service.client.upload_data(
                    audio_bytes, key, content_type=content_type, overwrite=True
                )

                return result.get("url", "")

            finally:
                # 清理临时文件
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            logger.error(f"上传音频到七牛云失败: {str(e)}")
            return None

    def _get_default_demo_text(self, voice_name: str) -> str:
        """
        根据音色名称获取默认示例文本

        Args:
            voice_name: 音色名称

        Returns:
            示例文本
        """
        # 根据音色名称返回不同的示例文本
        demo_texts = {
            "芊悦": "你好，我是芊悦，很高兴认识你！",
            "晨煦": "大家好，我是晨煦，阳光温暖的声音陪伴你。",
            "不吃鱼": "嗨，我是不吃鱼，虽然不会翘舌音，但声音很特别哦！",
            "詹妮弗": "Hello, I'm Jennifer, your professional English voice assistant.",
            "甜茶": "我是甜茶，节奏拉满，戏感炸裂，准备好听我的声音了吗？",
            "卡捷琳娜": "你好，我是卡捷琳娜，御姐音色，韵律回味十足。",
            "墨讲师": "大家好，我是墨讲师，严谨叙事，适合知识讲解。",
            "上海-阿珍": "侬好，我是上海阿珍，风风火火的上海阿姐。",
            "北京-晓东": "您好，我是北京晓东，胡同里长大的北京爷们儿。",
            "四川-晴儿": "你好，我是四川晴儿，甜到你心里的川妹子。",
            "南京-老李": "你好，我是南京老李，耐心的瑜伽老师。",
            "陕西-秦川": "你好，我是陕西秦川，面宽话短，心实声沉。",
            "闽南-阿杰": "你好，我是闽南阿杰，诙谐直爽的台湾哥仔。",
            "天津-李彼得": "你好，我是天津李彼得，相声捧哏风格。",
            "粤语-阿强": "你好，我是粤语阿强，幽默风趣，在线陪聊。",
            "粤语-阿清": "你好，我是粤语阿清，甜美港风闺蜜。",
            "四川-程川": "你好，我是四川程川，跳脱市井的成都男子。",
        }

        return demo_texts.get(voice_name, "你好，我是这个音色的示例，很高兴为你服务！")


# 创建服务实例
voice_demo_service = VoiceDemoService()
