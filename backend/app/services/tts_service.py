"""
Qwen3-TTS Flash 文本转语音服务
"""

from __future__ import annotations

import base64
import json
import logging
import os
import wave
from io import BytesIO
from typing import Optional

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class TTSRequest:
    def __init__(
        self,
        text: str,
        voice: Optional[str] = None,
        audio_format: str = "wav",
        sample_rate: int = 24000,
        model: Optional[str] = None,
        output_path: Optional[str] = None,
    ) -> None:
        self.text = text
        self.voice = voice
        self.audio_format = audio_format
        self.sample_rate = sample_rate
        self.model = model or "qwen3-tts-flash"
        self.output_path = output_path


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
        if not self.api_key:
            logger.warning("QWEN_API_KEY 未配置，TTS 请求将失败")
        self.model_default = "qwen3-tts-flash"
        self.default_voice = "Dylan"
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.endpoint = f"{self.base_url}/audio/speech"
        self.timeout = 60.0

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        if not req.text or not req.text.strip():
            raise ValueError("text 不能为空")
        if len(req.text) > 600:
            raise ValueError("Qwen3-TTS Flash 最大输入 600 字符，请自行切分后调用")

        voice = req.voice or self.default_voice
        audio_format = req.audio_format or "wav"
        sample_rate = req.sample_rate or 24000
        model = req.model or self.model_default

        payload = {
            "model": model,
            "input": req.text,
            "voice": voice,
            "format": audio_format,
            "sample_rate": sample_rate,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.endpoint, headers=headers, json=payload)

        if resp.status_code >= 400:
            self._raise_http_error(resp)

        content_type = resp.headers.get("Content-Type", "").lower()
        if content_type.startswith("audio/"):
            audio_bytes = resp.content
        else:
            audio_bytes = self._decode_audio_from_json(resp)
            content_type = self._infer_content_type(audio_format)

        if not audio_bytes:
            raise ValueError("未获取到音频数据")

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
    def _raise_http_error(resp: httpx.Response) -> None:
        try:
            data = resp.json()
            message = data.get("error", {}).get("message") or data.get("message")
        except Exception:
            message = resp.text
        raise httpx.HTTPStatusError(
            f"TTS 请求失败: {resp.status_code} - {message}",
            request=resp.request,
            response=resp,
        )

    @staticmethod
    def _decode_audio_from_json(resp: httpx.Response) -> Optional[bytes]:
        try:
            data = resp.json()
        except json.JSONDecodeError:
            return None
        b64 = data.get("audio")
        if isinstance(b64, str):
            try:
                return base64.b64decode(b64)
            except Exception:
                return None
        items = data.get("data")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                for key in ("b64", "audio", "data"):
                    if key in first and isinstance(first[key], str):
                        try:
                            return base64.b64decode(first[key])
                        except Exception:
                            return None
        return None

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