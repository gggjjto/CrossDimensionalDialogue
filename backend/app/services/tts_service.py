"""
Qwen3-TTS Flash 文本转语音服务
使用DashScope SDK
"""

from __future__ import annotations

import base64
import os
import wave
from io import BytesIO
from typing import Optional

import dashscope
from app.core.config import settings
from app.core.logger import get_logger
from dashscope import MultiModalConversation

logger = get_logger("tts_service")


class TTSRequest:
    def __init__(
        self,
        text: str,
        voice: Optional[str] = None,
        audio_format: str = "wav",
        sample_rate: int = 24000,
    ) -> None:
        self.text = text
        self.voice = voice
        self.audio_format = audio_format
        self.sample_rate = sample_rate
        self.model = "qwen3-tts-flash"
        self.output_path = None


class TTSResponse:
    def __init__(
        self,
        content_type: str,
        model: str,
        audio_bytes: Optional[bytes] = None,
        audio_path: Optional[str] = None,
        duration_sec: Optional[float] = None,
    ) -> None:
        self.content_type = content_type
        self.model = model
        self.audio_bytes = audio_bytes
        self.audio_path = audio_path
        self.duration_sec = duration_sec


class TTSService:
    def __init__(self) -> None:
        self.api_key = settings.QWEN_API_KEY
        self.model_default = "qwen3-tts-flash"
        self.default_voice = "Cherry"  # 使用Cherry作为默认音色

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        if not req.text or not req.text.strip():
            raise ValueError("text 不能为空")
        if len(req.text) > 600:
            raise ValueError("Qwen3-TTS Flash 最大输入 600 字符，请自行切分后调用")

        voice = req.voice or self.default_voice
        audio_format = req.audio_format
        sample_rate = req.sample_rate
        model = req.model

        try:
            logger.info(
                "开始TTS合成: 文本='%s...', 音色='%s', 模型='%s'", req.text[:50], voice, model
            )

            # 使用DashScope SDK调用TTS
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=model,
                text=req.text,
                voice=voice,
                language_type="Chinese",  # 建议与文本语种一致
                stream=False,
            )

            logger.info("TTS API调用成功，响应类型: %s", type(response))

            # 处理非流式响应
            logger.debug("响应对象属性: %s", dir(response))

            # 检查API调用是否成功
            if hasattr(response, "status_code") and response.status_code != 200:
                error_msg = "TTS API调用失败: %s" % response.status_code
                if hasattr(response, "message"):
                    error_msg += " - %s" % response.message
                if hasattr(response, "code"):
                    error_msg += " (错误码: %s)" % response.code
                logger.error(f"TTS API错误: {error_msg}")
                raise ValueError(error_msg)

            if not hasattr(response, "output") or response.output is None:
                logger.error("响应结构: %s", response)
                raise ValueError("TTS响应格式错误：缺少output字段")

            logger.debug("output对象属性: %s", dir(response.output))

            if not hasattr(response.output, "audio") or response.output.audio is None:
                logger.error("output结构: %s", response.output)
                raise ValueError("TTS响应格式错误：缺少audio字段")

            audio = response.output.audio
            logger.debug("audio对象属性: %s", dir(audio))

            # 检查是否有音频数据
            if not hasattr(audio, "data") or not audio.data:
                # 如果没有data字段，尝试使用url字段
                if hasattr(audio, "url") and audio.url:
                    logger.info("音频数据通过URL提供: %s", audio.url)
                    # 这里需要下载URL中的音频数据
                    import httpx

                    async with httpx.AsyncClient() as client:
                        audio_resp = await client.get(audio.url)
                        if audio_resp.status_code == 200:
                            audio_bytes = audio_resp.content
                        else:
                            raise ValueError("下载音频失败: %s" % audio_resp.status_code)
                else:
                    raise ValueError("TTS响应中没有音频数据")
            else:
                # 使用base64编码的音频数据
                try:
                    audio_bytes = base64.b64decode(audio.data)
                    logger.info("成功解码音频数据，大小: %s 字节", len(audio_bytes))
                except Exception as e:
                    raise ValueError("解码音频数据失败: %s" % str(e))

            if not audio_bytes:
                raise ValueError("未获取到音频数据")

            # 确定内容类型
            content_type = self._infer_content_type(audio_format)

            # 计算音频时长
            duration = self._maybe_calculate_wav_duration(audio_bytes, content_type)

            if req.output_path:
                self._ensure_parent_dir(req.output_path)
                with open(req.output_path, "wb") as f:
                    f.write(audio_bytes)
                return TTSResponse(
                    content_type=content_type,
                    model=model,
                    audio_path=req.output_path,
                    duration_sec=duration,
                )

            return TTSResponse(
                content_type=content_type,
                model=model,
                audio_bytes=audio_bytes,
                duration_sec=duration,
            )

        except Exception as e:
            logger.error("TTS合成失败: %s", str(e))
            raise ValueError("TTS合成失败")

    @staticmethod
    def _infer_content_type(fmt: str) -> str:
        if fmt == "wav":
            return "audio/wav"
        if fmt == "mp3":
            return "audio/mpeg"
        if fmt == "pcm":
            return "audio/pcm"
        if fmt == "opus":
            return "audio/opus"
        return "application/octet-stream"

    @staticmethod
    def _ensure_parent_dir(path: str) -> None:
        parent = os.path.dirname(os.path.abspath(path))
        if parent and not os.path.exists(parent):
            os.makedirs(parent, exist_ok=True)

    @staticmethod
    def _maybe_calculate_wav_duration(
        audio_bytes: bytes, content_type: str
    ) -> Optional[float]:
        if not content_type.startswith("audio/wav"):
            return None
        try:
            with wave.open(BytesIO(audio_bytes), "rb") as w:
                frames = w.getnframes()
                rate = w.getframerate()
                if rate <= 0:
                    return None
                return frames / float(rate)
        except Exception:
            return None


tts_service = TTSService()
