"""
Qwen3-ASR 语音识别服务（使用DashScope SDK）。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import dashscope
from dashscope import MultiModalConversation

from app.core.config import settings


logger = logging.getLogger(__name__)


class STTRequest:
    """语音转文本请求。"""

    def __init__(
        self,
        audio_url: str,
        model: Optional[str] = 'qwen3-asr-flash',
        prompt: Optional[str] = None,
        language: Optional[str] = 'zh',
        enable_lid: bool = True,
        enable_itn: bool = False,
    ) -> None:
        self.audio_url = audio_url
        self.model = model
        self.prompt = prompt
        self.language = language
        self.enable_lid = enable_lid
        self.enable_itn = enable_itn


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
        else:
            dashscope.api_key = self.api_key
        self.model_default = "qwen3-asr-flash"

    async def transcribe(self, req: STTRequest) -> STTResponse:
        """
        语音转文本识别

        Args:
            req: STT请求对象

        Returns:
            STTResponse: 识别结果

        Raises:
            ValueError: 当音频URL无效或API调用失败时
        """
        if not req.audio_url or not req.audio_url.startswith("http"):
            raise ValueError("audio_url 必须是公网可访问的 URL")

        model = req.model or self.model_default

        try:
            logger.info(f"开始ASR识别: 音频URL='{req.audio_url}', 模型='{model}'")

            # 构建消息格式
            messages = [
                {
                    "role": "system",
                    "content": [{"text": req.prompt or ""}],  # 系统提示词
                },
                {"role": "user", "content": [{"audio": req.audio_url}]},  # 音频URL
            ]

            # 构建ASR选项
            asr_options = {
                "enable_lid": req.enable_lid,
                "enable_itn": req.enable_itn,
            }
            if req.language:
                asr_options["language"] = req.language

            # 调用DashScope SDK
            response = MultiModalConversation.call(
                api_key=self.api_key,
                model=model,
                messages=messages,
                result_format="message",
                asr_options=asr_options,
            )

            logger.info(f"ASR API调用成功，响应类型: {type(response)}")

            # 检查API调用是否成功
            if hasattr(response, "status_code") and response.status_code != 200:
                error_msg = f"ASR API调用失败: {response.status_code}"
                if hasattr(response, "message"):
                    error_msg += f" - {response.message}"
                if hasattr(response, "code"):
                    error_msg += f" (错误码: {response.code})"
                logger.error(f"ASR API错误: {error_msg}")
                raise ValueError(error_msg)

            # 处理响应
            text, language, duration, words = self._extract_result_fields(response)

            logger.info(f"ASR识别完成: 文本长度={len(text)}, 语言={language}")

            return STTResponse(
                text=text,
                model=model,
                language=language,
                duration_sec=duration,
                words=words,
                raw=response.__dict__ if hasattr(response, "__dict__") else {},
            )

        except Exception as e:
            logger.error(f"ASR识别失败: {str(e)}")
            raise ValueError(f"ASR识别失败: {str(e)}")

    @staticmethod
    def _extract_result_fields(
        response: Any,
    ) -> tuple[str, Optional[str], Optional[float], Optional[List[Dict[str, Any]]]]:
        """
        从DashScope SDK响应中提取核心字段
        """
        text = ""
        language = None
        duration = None
        words = None

        try:
            # 检查响应结构
            if not hasattr(response, "output") or response.output is None:
                logger.error(f"ASR响应格式错误：缺少output字段，响应: {response}")
                return text, language, duration, words

            output = response.output

            # 提取文本内容
            if hasattr(output, "choices") and output.choices:
                choices = output.choices
                if isinstance(choices, list) and len(choices) > 0:
                    first_choice = choices[0]
                    if hasattr(first_choice, "message") and first_choice.message:
                        message = first_choice.message
                        if hasattr(message, "content") and message.content:
                            content = message.content
                            if isinstance(content, list):
                                text_parts = []
                                for part in content:
                                    if isinstance(part, dict) and "text" in part:
                                        text_parts.append(part["text"])
                                    elif isinstance(part, str):
                                        text_parts.append(part)
                                text = "".join(text_parts).strip()
                            elif isinstance(content, str):
                                text = content.strip()

            # 提取语言信息
            if hasattr(output, "choices") and output.choices:
                choices = output.choices
                if isinstance(choices, list) and len(choices) > 0:
                    first_choice = choices[0]
                    if hasattr(first_choice, "message") and first_choice.message:
                        message = first_choice.message
                        if hasattr(message, "annotations") and message.annotations:
                            annotations = message.annotations
                            if isinstance(annotations, list) and len(annotations) > 0:
                                first_annotation = annotations[0]
                                if (
                                    isinstance(first_annotation, dict)
                                    and "language" in first_annotation
                                ):
                                    language = first_annotation["language"]

            # 提取时长信息
            if hasattr(response, "usage") and response.usage:
                usage = response.usage
                if hasattr(usage, "seconds"):
                    duration = float(usage.seconds)
                elif isinstance(usage, dict) and "seconds" in usage:
                    duration = float(usage["seconds"])

            logger.debug(f"提取结果: 文本='{text}', 语言={language}, 时长={duration}")

        except Exception as e:
            logger.error(f"提取ASR结果字段失败: {str(e)}")

        return text, language, duration, words


# 全局实例
stt_service = STTService()
