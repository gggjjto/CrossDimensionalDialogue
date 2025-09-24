"""
Qwen3-ASR 录音文件识别服务（简化版，风格对齐 llm_service）。
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)


class STTRequest:
    """语音转文本请求。"""

    def __init__(
        self,
        audio_url: str,
        model: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: Optional[float] = None,
    ) -> None:
        self.audio_url = audio_url
        self.model = model or "qwen3-asr-flash"
        self.prompt = prompt
        self.response_format = response_format
        self.temperature = temperature


class STTResponse:
    """语音转文本响应。"""

    def __init__(
        self,
        text: str,
        model: str,
        language: Optional[str] = None,
        duration_sec: Optional[float] = None,
        words: Optional[List[Dict[str, Any]]] = None,
        raw: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.text = text
        self.model = model
        self.language = language
        self.duration_sec = duration_sec
        self.words = words or []
        self.raw = raw or {}


class STTService:
    """Qwen3-ASR 语音识别服务。"""

    def __init__(self) -> None:
        self.api_key = settings.QWEN_API_KEY
        if not self.api_key:
            logger.warning("QWEN_API_KEY 未配置，ASR 请求将失败")
        self.model_default = "qwen3-asr-flash"
        self.base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.endpoint = f"{self.base_url}/audio/transcriptions"
        self.timeout = 120.0

    async def transcribe(self, req: STTRequest) -> STTResponse:
        if not req.audio_url or not req.audio_url.startswith("http"):
            raise ValueError("audio_url 必须是公网可访问的 URL")

        model = req.model or self.model_default

        payload: Dict[str, Any] = {
            "model": model,
            "audio_url": req.audio_url,
        }
        if req.prompt:
            payload["prompt"] = req.prompt
        if req.response_format:
            payload["response_format"] = req.response_format
        if req.temperature is not None:
            payload["temperature"] = req.temperature

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(self.endpoint, headers=headers, json=payload)

        if resp.status_code >= 400:
            self._raise_http_error(resp)

        data = self._safe_json(resp)
        text, language, duration, words = self._extract_result_fields(data)
        return STTResponse(
            text=text,
            model=model,
            language=language,
            duration_sec=duration,
            words=words,
            raw=data,
        )

    @staticmethod
    def _safe_json(resp: httpx.Response) -> Dict[str, Any]:
        try:
            return resp.json()
        except json.JSONDecodeError:
            return {"raw": resp.text}

    @staticmethod
    def _raise_http_error(resp: httpx.Response) -> None:
        try:
            data = resp.json()
            message = (
                data.get("error", {}).get("message")
                or data.get("message")
                or data.get("detail")
            )
        except Exception:
            message = resp.text
        raise httpx.HTTPStatusError(
            f"ASR 请求失败: {resp.status_code} - {message}",
            request=resp.request,
            response=resp,
        )

    @staticmethod
    def _extract_result_fields(
        data: Dict[str, Any],
    ) -> tuple[str, Optional[str], Optional[float], Optional[List[Dict[str, Any]]]]:
        """
        按固定返回结构提取核心字段，不做其他格式适配。
        """
        output = data.get("output") or {}
        usage = data.get("usage") or {}

        # 文本：拼接 choices[0].message.content[].text
        text: str = ""
        choices = output.get("choices") or []
        if isinstance(choices, list) and choices:
            first = choices[0] or {}
            message = first.get("message") or {}
            content = message.get("content") or []
            if isinstance(content, list):
                parts: List[str] = []
                for part in content:
                    if isinstance(part, dict) and isinstance(part.get("text"), str):
                        parts.append(part["text"])
                    elif isinstance(part, str):
                        parts.append(part)
                text = "".join(parts).strip()

        # 语言：choices[0].message.annotations[*].language
        language: Optional[str] = None
        if isinstance(choices, list) and choices:
            msg = (choices[0] or {}).get("message") or {}
            annotations = msg.get("annotations") or []
            if isinstance(annotations, list) and annotations:
                lang = annotations[0].get("language")
                if isinstance(lang, str):
                    language = lang

        # 时长：usage.seconds
        duration: Optional[float] = None
        seconds = usage.get("seconds")
        if isinstance(seconds, (int, float)):
            duration = float(seconds)

        # 词级：本结构未提供
        words: Optional[List[Dict[str, Any]]] = None

        return text, language, duration, words


# 全局实例，风格与 llm_service.py 对齐
stt_service = STTService()
