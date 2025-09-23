import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile
import os

from app.models.voice import (
    SpeechRecognitionResult,
    VoiceLanguage,
    AudioFormat,
    AudioQuality,
    AudioProcessingStatus,
)
from app.core.config import settings


class STTService:
    """语音转文本服务"""

    def __init__(self):
        self.supported_languages = {
            VoiceLanguage.ZH_CN: "zh-CN",
            VoiceLanguage.ZH_TW: "zh-TW",
            VoiceLanguage.EN_US: "en-US",
            VoiceLanguage.EN_GB: "en-GB",
            VoiceLanguage.JA_JP: "ja-JP",
            VoiceLanguage.KO_KR: "ko-KR",
            VoiceLanguage.ES_ES: "es-ES",
            VoiceLanguage.FR_FR: "fr-FR",
            VoiceLanguage.DE_DE: "de-DE",
            VoiceLanguage.RU_RU: "ru-RU",
        }

        # 支持的音频格式
        self.supported_formats = {
            AudioFormat.MP3: [".mp3"],
            AudioFormat.WAV: [".wav"],
            AudioFormat.AAC: [".aac", ".m4a"],
            AudioFormat.OGG: [".ogg"],
            AudioFormat.FLAC: [".flac"],
        }

    async def transcribe_audio(
        self,
        audio_file_path: str,
        language: VoiceLanguage = VoiceLanguage.ZH_CN,
        enable_auto_detection: bool = False,
        enable_punctuation: bool = True,
        enable_word_timestamps: bool = False,
        custom_vocabulary: Optional[List[str]] = None,
    ) -> SpeechRecognitionResult:
        """
        将音频文件转换为文本

        Args:
            audio_file_path: 音频文件路径
            language: 语音语言
            enable_auto_detection: 是否启用自动语言检测
            enable_punctuation: 是否启用标点符号
            enable_word_timestamps: 是否启用词级时间戳
            custom_vocabulary: 自定义词汇表

        Returns:
            SpeechRecognitionResult: 识别结果
        """
        try:
            # 验证音频文件
            if not os.path.exists(audio_file_path):
                raise FileNotFoundError(f"音频文件不存在: {audio_file_path}")

            # 检查文件格式
            file_extension = Path(audio_file_path).suffix.lower()
            if not self._is_supported_format(file_extension):
                raise ValueError(f"不支持的音频格式: {file_extension}")

            # 获取音频信息
            audio_info = await self._get_audio_info(audio_file_path)

            # 根据配置选择STT引擎
            if settings.STT_ENGINE == "openai":
                result = await self._transcribe_with_openai(
                    audio_file_path,
                    language,
                    enable_auto_detection,
                    enable_punctuation,
                    enable_word_timestamps,
                    custom_vocabulary,
                )
            elif settings.STT_ENGINE == "azure":
                result = await self._transcribe_with_azure(
                    audio_file_path,
                    language,
                    enable_auto_detection,
                    enable_punctuation,
                    enable_word_timestamps,
                    custom_vocabulary,
                )
            elif settings.STT_ENGINE == "google":
                result = await self._transcribe_with_google(
                    audio_file_path,
                    language,
                    enable_auto_detection,
                    enable_punctuation,
                    enable_word_timestamps,
                    custom_vocabulary,
                )
            else:
                # 使用本地Whisper模型
                result = await self._transcribe_with_whisper(
                    audio_file_path,
                    language,
                    enable_auto_detection,
                    enable_punctuation,
                    enable_word_timestamps,
                    custom_vocabulary,
                )

            # 添加音频信息到结果
            result.duration = audio_info.get("duration", 0.0)
            result.word_count = len(result.text.split())

            return result

        except Exception as e:
            raise Exception(f"语音识别失败: {str(e)}")

    async def _transcribe_with_openai(
        self,
        audio_file_path: str,
        language: VoiceLanguage,
        enable_auto_detection: bool,
        enable_punctuation: bool,
        enable_word_timestamps: bool,
        custom_vocabulary: Optional[List[str]],
    ) -> SpeechRecognitionResult:
        """使用OpenAI Whisper API进行语音识别"""
        try:
            import openai

            # 设置OpenAI客户端
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            # 准备请求参数
            with open(audio_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=self.supported_languages.get(language, "zh-CN"),
                    response_format="verbose_json",
                    timestamp_granularities=(
                        ["word"] if enable_word_timestamps else None
                    ),
                )

            # 处理结果
            text = transcript.text
            confidence = getattr(
                transcript, "confidence", 0.9
            )  # OpenAI不直接提供置信度

            # 构建分段结果
            segments = []
            if hasattr(transcript, "words") and enable_word_timestamps:
                for word in transcript.words:
                    segments.append(
                        {
                            "word": word.word,
                            "start": word.start,
                            "end": word.end,
                            "confidence": getattr(word, "confidence", confidence),
                        }
                    )

            return SpeechRecognitionResult(
                text=text,
                confidence=confidence,
                language=language,
                duration=0.0,  # 将在调用方设置
                word_count=0,  # 将在调用方设置
                segments=segments if segments else None,
                voice_metadata={
                    "engine": "openai",
                    "model": "whisper-1",
                    "auto_detection": enable_auto_detection,
                    "punctuation": enable_punctuation,
                    "word_timestamps": enable_word_timestamps,
                    "custom_vocabulary": custom_vocabulary,
                },
            )

        except Exception as e:
            raise Exception(f"OpenAI语音识别失败: {str(e)}")

    async def _transcribe_with_azure(
        self,
        audio_file_path: str,
        language: VoiceLanguage,
        enable_auto_detection: bool,
        enable_punctuation: bool,
        enable_word_timestamps: bool,
        custom_vocabulary: Optional[List[str]],
    ) -> SpeechRecognitionResult:
        """使用Azure Speech Services进行语音识别"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            # 设置Azure配置
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION,
            )
            speech_config.speech_recognition_language = self.supported_languages.get(
                language, "zh-CN"
            )

            # 设置音频配置
            audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)

            # 创建语音识别器
            speech_recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config, audio_config=audio_config
            )

            # 执行识别
            result = await asyncio.get_event_loop().run_in_executor(
                None, speech_recognizer.recognize_once
            )

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                text = result.text
                confidence = 0.9  # Azure不直接提供置信度

                return SpeechRecognitionResult(
                    text=text,
                    confidence=confidence,
                    language=language,
                    duration=0.0,
                    word_count=0,
                    voice_metadata={
                        "engine": "azure",
                        "auto_detection": enable_auto_detection,
                        "punctuation": enable_punctuation,
                        "word_timestamps": enable_word_timestamps,
                        "custom_vocabulary": custom_vocabulary,
                    },
                )
            else:
                raise Exception(f"Azure语音识别失败: {result.reason}")

        except Exception as e:
            raise Exception(f"Azure语音识别失败: {str(e)}")

    async def _transcribe_with_google(
        self,
        audio_file_path: str,
        language: VoiceLanguage,
        enable_auto_detection: bool,
        enable_punctuation: bool,
        enable_word_timestamps: bool,
        custom_vocabulary: Optional[List[str]],
    ) -> SpeechRecognitionResult:
        """使用Google Cloud Speech-to-Text进行语音识别"""
        try:
            from google.cloud import speech

            # 设置Google客户端
            client = speech.SpeechClient()

            # 读取音频文件
            with open(audio_file_path, "rb") as audio_file:
                content = audio_file.read()

            # 配置识别参数
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=self.supported_languages.get(language, "zh-CN"),
                enable_automatic_punctuation=enable_punctuation,
                enable_word_time_offsets=enable_word_timestamps,
                alternative_language_codes=(
                    ["en-US", "zh-CN"] if enable_auto_detection else None
                ),
            )

            # 执行识别
            audio = speech.RecognitionAudio(content=content)
            response = await asyncio.get_event_loop().run_in_executor(
                None, client.recognize, config, audio
            )

            if response.results:
                result = response.results[0]
                text = result.alternatives[0].transcript
                confidence = result.alternatives[0].confidence

                # 构建分段结果
                segments = []
                if enable_word_timestamps and result.alternatives[0].words:
                    for word in result.alternatives[0].words:
                        segments.append(
                            {
                                "word": word.word,
                                "start": word.start_time.total_seconds(),
                                "end": word.end_time.total_seconds(),
                                "confidence": word.confidence,
                            }
                        )

                return SpeechRecognitionResult(
                    text=text,
                    confidence=confidence,
                    language=language,
                    duration=0.0,
                    word_count=0,
                    segments=segments if segments else None,
                    voice_metadata={
                        "engine": "google",
                        "auto_detection": enable_auto_detection,
                        "punctuation": enable_punctuation,
                        "word_timestamps": enable_word_timestamps,
                        "custom_vocabulary": custom_vocabulary,
                    },
                )
            else:
                raise Exception("Google语音识别未返回结果")

        except Exception as e:
            raise Exception(f"Google语音识别失败: {str(e)}")

    async def _transcribe_with_whisper(
        self,
        audio_file_path: str,
        language: VoiceLanguage,
        enable_auto_detection: bool,
        enable_punctuation: bool,
        enable_word_timestamps: bool,
        custom_vocabulary: Optional[List[str]],
    ) -> SpeechRecognitionResult:
        """使用本地Whisper模型进行语音识别"""
        try:
            import whisper

            # 加载模型
            model = whisper.load_model(settings.WHISPER_MODEL_SIZE)

            # 执行识别
            result = await asyncio.get_event_loop().run_in_executor(
                None,
                model.transcribe,
                audio_file_path,
                language=self.supported_languages.get(language, "zh"),
                word_timestamps=enable_word_timestamps,
            )

            text = result["text"]
            confidence = 0.9  # Whisper不直接提供置信度

            # 构建分段结果
            segments = []
            if enable_word_timestamps and "segments" in result:
                for segment in result["segments"]:
                    if "words" in segment:
                        for word in segment["words"]:
                            segments.append(
                                {
                                    "word": word["word"],
                                    "start": word["start"],
                                    "end": word["end"],
                                    "confidence": word.get("probability", confidence),
                                }
                            )

            return SpeechRecognitionResult(
                text=text,
                confidence=confidence,
                language=language,
                duration=0.0,
                word_count=0,
                segments=segments if segments else None,
                voice_metadata={
                    "engine": "whisper",
                    "model": settings.WHISPER_MODEL_SIZE,
                    "auto_detection": enable_auto_detection,
                    "punctuation": enable_punctuation,
                    "word_timestamps": enable_word_timestamps,
                    "custom_vocabulary": custom_vocabulary,
                },
            )

        except Exception as e:
            raise Exception(f"Whisper语音识别失败: {str(e)}")

    def _is_supported_format(self, file_extension: str) -> bool:
        """检查音频格式是否支持"""
        for format_type, extensions in self.supported_formats.items():
            if file_extension in extensions:
                return True
        return False

    async def _get_audio_info(self, audio_file_path: str) -> Dict[str, Any]:
        """获取音频文件信息"""
        try:
            import librosa

            # 使用librosa获取音频信息
            y, sr = await asyncio.get_event_loop().run_in_executor(
                None, librosa.load, audio_file_path
            )

            duration = len(y) / sr

            return {
                "duration": duration,
                "sample_rate": sr,
                "channels": 1 if y.ndim == 1 else y.shape[0],
                "samples": len(y),
            }

        except Exception as e:
            # 如果librosa不可用，返回基本信息
            file_size = os.path.getsize(audio_file_path)
            return {
                "duration": 0.0,
                "sample_rate": 16000,  # 默认值
                "channels": 1,
                "file_size": file_size,
            }

    async def detect_language(self, audio_file_path: str) -> VoiceLanguage:
        """自动检测音频语言"""
        try:
            # 使用Whisper进行语言检测
            import whisper

            model = whisper.load_model("base")
            result = await asyncio.get_event_loop().run_in_executor(
                None, model.transcribe, audio_file_path, language=None
            )

            detected_language = result.get("language", "zh")

            # 映射到我们的语言枚举
            language_mapping = {
                "zh": VoiceLanguage.ZH_CN,
                "en": VoiceLanguage.EN_US,
                "ja": VoiceLanguage.JA_JP,
                "ko": VoiceLanguage.KO_KR,
                "es": VoiceLanguage.ES_ES,
                "fr": VoiceLanguage.FR_FR,
                "de": VoiceLanguage.DE_DE,
                "ru": VoiceLanguage.RU_RU,
            }

            return language_mapping.get(detected_language, VoiceLanguage.ZH_CN)

        except Exception as e:
            # 如果检测失败，返回默认语言
            return VoiceLanguage.ZH_CN

    async def validate_audio_quality(self, audio_file_path: str) -> Dict[str, Any]:
        """验证音频质量"""
        try:
            import librosa

            # 加载音频
            y, sr = await asyncio.get_event_loop().run_in_executor(
                None, librosa.load, audio_file_path
            )

            # 计算质量指标
            duration = len(y) / sr
            rms = float(librosa.feature.rms(y=y)[0].mean())
            zero_crossing_rate = float(librosa.feature.zero_crossing_rate(y)[0].mean())

            # 质量评分
            quality_score = 0.0
            issues = []

            # 检查音量
            if rms < 0.01:
                quality_score += 1.0
                issues.append("音量过低")
            elif rms > 0.5:
                quality_score += 1.0
                issues.append("音量过高")
            else:
                quality_score += 3.0

            # 检查时长
            if duration < 0.5:
                quality_score += 1.0
                issues.append("音频过短")
            elif duration > 300:
                quality_score += 1.0
                issues.append("音频过长")
            else:
                quality_score += 2.0

            # 检查采样率
            if sr < 8000:
                quality_score += 1.0
                issues.append("采样率过低")
            elif sr >= 16000:
                quality_score += 2.0

            # 检查零交叉率（噪音指标）
            if zero_crossing_rate > 0.1:
                quality_score += 1.0
                issues.append("可能存在噪音")
            else:
                quality_score += 2.0

            return {
                "quality_score": min(quality_score, 10.0),
                "duration": duration,
                "sample_rate": sr,
                "rms": rms,
                "zero_crossing_rate": zero_crossing_rate,
                "issues": issues,
                "is_good_quality": quality_score >= 6.0,
            }

        except Exception as e:
            return {
                "quality_score": 0.0,
                "duration": 0.0,
                "sample_rate": 0,
                "rms": 0.0,
                "zero_crossing_rate": 0.0,
                "issues": [f"质量检测失败: {str(e)}"],
                "is_good_quality": False,
            }


# 全局STT服务实例
stt_service = STTService()
