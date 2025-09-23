import asyncio
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pathlib import Path
import tempfile
import os

from app.models.voice import (
    VoiceSynthesisRequest,
    VoiceSynthesisResult,
    VoiceLanguage,
    VoiceGender,
    VoiceEmotion,
    AudioFormat,
    AudioQuality,
)
from app.core.config import settings


class TTSService:
    """文本转语音服务"""

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
            AudioFormat.MP3: "mp3",
            AudioFormat.WAV: "wav",
            AudioFormat.AAC: "aac",
            AudioFormat.OGG: "ogg",
            AudioFormat.M4A: "m4a",
            AudioFormat.FLAC: "flac",
        }

        # 情感到语音参数的映射
        self.emotion_mappings = {
            VoiceEmotion.NEUTRAL: {"rate": 1.0, "pitch": 1.0, "volume": 1.0},
            VoiceEmotion.HAPPY: {"rate": 1.1, "pitch": 1.1, "volume": 1.0},
            VoiceEmotion.SAD: {"rate": 0.9, "pitch": 0.9, "volume": 0.9},
            VoiceEmotion.ANGRY: {"rate": 1.2, "pitch": 1.2, "volume": 1.1},
            VoiceEmotion.EXCITED: {"rate": 1.3, "pitch": 1.3, "volume": 1.1},
            VoiceEmotion.CALM: {"rate": 0.8, "pitch": 0.9, "volume": 0.9},
            VoiceEmotion.CONFUSED: {"rate": 0.9, "pitch": 1.1, "volume": 0.9},
            VoiceEmotion.SURPRISED: {"rate": 1.2, "pitch": 1.4, "volume": 1.1},
        }

    async def synthesize_speech(
        self, request: VoiceSynthesisRequest, output_dir: str = None
    ) -> VoiceSynthesisResult:
        """
        将文本转换为语音

        Args:
            request: 语音合成请求
            output_dir: 输出目录

        Returns:
            VoiceSynthesisResult: 合成结果
        """
        try:
            # 验证输入
            if not request.text.strip():
                raise ValueError("文本内容不能为空")

            if len(request.text) > 5000:
                raise ValueError("文本长度不能超过5000字符")

            # 设置输出目录
            if output_dir is None:
                output_dir = tempfile.mkdtemp()

            # 生成输出文件名
            output_filename = f"tts_{uuid.uuid4().hex}.{self.supported_formats[request.output_format]}"
            output_path = os.path.join(output_dir, output_filename)

            # 根据配置选择TTS引擎
            if settings.TTS_ENGINE == "openai":
                result = await self._synthesize_with_openai(request, output_path)
            elif settings.TTS_ENGINE == "azure":
                result = await self._synthesize_with_azure(request, output_path)
            elif settings.TTS_ENGINE == "google":
                result = await self._synthesize_with_google(request, output_path)
            elif settings.TTS_ENGINE == "elevenlabs":
                result = await self._synthesize_with_elevenlabs(request, output_path)
            else:
                # 使用本地TTS引擎
                result = await self._synthesize_with_local(request, output_path)

            # 获取文件信息
            file_size = os.path.getsize(output_path)

            # 计算音频时长
            duration = await self._get_audio_duration(output_path)

            return VoiceSynthesisResult(
                audio_url=output_path,
                duration=duration,
                file_size=file_size,
                format=request.output_format,
                quality=request.output_quality,
                voice_metadata={
                    "engine": settings.TTS_ENGINE,
                    "text_length": len(request.text),
                    "emotion": request.emotion.value if request.emotion else "neutral",
                    "speed": request.speed,
                    "pitch": request.pitch,
                    "volume": request.volume,
                },
            )

        except Exception as e:
            raise Exception(f"语音合成失败: {str(e)}")

    async def _synthesize_with_openai(
        self, request: VoiceSynthesisRequest, output_path: str
    ) -> None:
        """使用OpenAI TTS进行语音合成"""
        try:
            import openai

            # 设置OpenAI客户端
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            # 选择语音模型
            voice_model = self._get_openai_voice(request)

            # 执行合成
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice_model,
                input=request.text,
                response_format=self.supported_formats[request.output_format],
            )

            # 保存音频文件
            with open(output_path, "wb") as f:
                f.write(response.content)

        except Exception as e:
            raise Exception(f"OpenAI TTS失败: {str(e)}")

    async def _synthesize_with_azure(
        self, request: VoiceSynthesisRequest, output_path: str
    ) -> None:
        """使用Azure Speech Services进行语音合成"""
        try:
            import azure.cognitiveservices.speech as speechsdk

            # 设置Azure配置
            speech_config = speechsdk.SpeechConfig(
                subscription=settings.AZURE_SPEECH_KEY,
                region=settings.AZURE_SPEECH_REGION,
            )

            # 设置语音参数
            voice_name = self._get_azure_voice(request)
            speech_config.speech_synthesis_voice_name = voice_name

            # 设置输出格式
            speech_config.set_speech_synthesis_output_format(
                speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
                if request.output_format == AudioFormat.MP3
                else speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
            )

            # 创建语音合成器
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, audio_config=None
            )

            # 执行合成
            result = await asyncio.get_event_loop().run_in_executor(
                None, synthesizer.speak_text_async, request.text
            )

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # 保存音频文件
                with open(output_path, "wb") as f:
                    f.write(result.audio_data)
            else:
                raise Exception(f"Azure TTS失败: {result.reason}")

        except Exception as e:
            raise Exception(f"Azure TTS失败: {str(e)}")

    async def _synthesize_with_google(
        self, request: VoiceSynthesisRequest, output_path: str
    ) -> None:
        """使用Google Cloud Text-to-Speech进行语音合成"""
        try:
            from google.cloud import texttospeech

            # 设置Google客户端
            client = texttospeech.TextToSpeechClient()

            # 设置输入文本
            synthesis_input = texttospeech.SynthesisInput(text=request.text)

            # 设置语音参数
            voice = texttospeech.VoiceSelectionParams(
                language_code=self.supported_languages.get(
                    request.voice_config_id, VoiceLanguage.ZH_CN
                ),
                name=self._get_google_voice(request),
                ssml_gender=(
                    texttospeech.SsmlVoiceGender.MALE
                    if request.gender == VoiceGender.MALE
                    else texttospeech.SsmlVoiceGender.FEMALE
                ),
            )

            # 设置音频配置
            audio_config = texttospeech.AudioConfig(
                audio_encoding=(
                    texttospeech.AudioEncoding.MP3
                    if request.output_format == AudioFormat.MP3
                    else texttospeech.AudioEncoding.LINEAR16
                )
            )

            # 执行合成
            response = await asyncio.get_event_loop().run_in_executor(
                None, client.synthesize_speech, synthesis_input, voice, audio_config
            )

            # 保存音频文件
            with open(output_path, "wb") as f:
                f.write(response.audio_content)

        except Exception as e:
            raise Exception(f"Google TTS失败: {str(e)}")

    async def _synthesize_with_elevenlabs(
        self, request: VoiceSynthesisRequest, output_path: str
    ) -> None:
        """使用ElevenLabs进行语音合成"""
        try:
            import requests

            # 设置请求参数
            url = (
                f"https://api.elevenlabs.io/v1/text-to-speech/{request.voice_config_id}"
            )

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": settings.ELEVENLABS_API_KEY,
            }

            data = {
                "text": request.text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.0,
                    "use_speaker_boost": True,
                },
            }

            # 执行请求
            response = await asyncio.get_event_loop().run_in_executor(
                None, requests.post, url, headers, data
            )

            if response.status_code == 200:
                # 保存音频文件
                with open(output_path, "wb") as f:
                    f.write(response.content)
            else:
                raise Exception(f"ElevenLabs TTS失败: {response.status_code}")

        except Exception as e:
            raise Exception(f"ElevenLabs TTS失败: {str(e)}")

    async def _synthesize_with_local(
        self, request: VoiceSynthesisRequest, output_path: str
    ) -> None:
        """使用本地TTS引擎进行语音合成"""
        try:
            import pyttsx3

            # 初始化TTS引擎
            engine = pyttsx3.init()

            # 设置语音参数
            voices = engine.getProperty("voices")
            if voices:
                # 根据语言和性别选择语音
                voice = self._select_local_voice(voices, request)
                if voice:
                    engine.setProperty("voice", voice.id)

            # 设置语速、音调和音量
            rate = int(200 * (request.speed or 1.0))
            volume = request.volume or 1.0

            engine.setProperty("rate", rate)
            engine.setProperty("volume", volume)

            # 执行合成
            await asyncio.get_event_loop().run_in_executor(
                None, engine.save_to_file, request.text, output_path
            )

            # 等待合成完成
            engine.runAndWait()

        except Exception as e:
            raise Exception(f"本地TTS失败: {str(e)}")

    def _get_openai_voice(self, request: VoiceSynthesisRequest) -> str:
        """获取OpenAI语音模型"""
        # OpenAI支持的语音模型
        voices = {
            VoiceGender.MALE: ["alloy", "echo", "fable", "onyx"],
            VoiceGender.FEMALE: ["nova", "shimmer"],
        }

        gender = request.gender or VoiceGender.MALE
        voice_list = voices.get(gender, voices[VoiceGender.MALE])

        # 根据情感选择语音
        if request.emotion == VoiceEmotion.HAPPY:
            return voice_list[0]  # 选择第一个
        elif request.emotion == VoiceEmotion.SAD:
            return voice_list[-1]  # 选择最后一个
        else:
            return voice_list[0]

    def _get_azure_voice(self, request: VoiceSynthesisRequest) -> str:
        """获取Azure语音模型"""
        # Azure语音模型映射
        voice_mapping = {
            VoiceLanguage.ZH_CN: {
                VoiceGender.MALE: "zh-CN-YunxiNeural",
                VoiceGender.FEMALE: "zh-CN-XiaoxiaoNeural",
            },
            VoiceLanguage.EN_US: {
                VoiceGender.MALE: "en-US-GuyNeural",
                VoiceGender.FEMALE: "en-US-AriaNeural",
            },
            VoiceLanguage.EN_GB: {
                VoiceGender.MALE: "en-GB-RyanNeural",
                VoiceGender.FEMALE: "en-GB-SoniaNeural",
            },
        }

        language = request.voice_config_id or VoiceLanguage.ZH_CN
        gender = request.gender or VoiceGender.MALE

        return voice_mapping.get(language, voice_mapping[VoiceLanguage.ZH_CN]).get(
            gender, "zh-CN-XiaoxiaoNeural"
        )

    def _get_google_voice(self, request: VoiceSynthesisRequest) -> str:
        """获取Google语音模型"""
        # Google语音模型映射
        voice_mapping = {
            VoiceLanguage.ZH_CN: {
                VoiceGender.MALE: "zh-CN-Wavenet-A",
                VoiceGender.FEMALE: "zh-CN-Wavenet-C",
            },
            VoiceLanguage.EN_US: {
                VoiceGender.MALE: "en-US-Wavenet-A",
                VoiceGender.FEMALE: "en-US-Wavenet-C",
            },
        }

        language = request.voice_config_id or VoiceLanguage.ZH_CN
        gender = request.gender or VoiceGender.MALE

        return voice_mapping.get(language, voice_mapping[VoiceLanguage.ZH_CN]).get(
            gender, "zh-CN-Wavenet-C"
        )

    def _select_local_voice(
        self, voices: List, request: VoiceSynthesisRequest
    ) -> Optional[Any]:
        """选择本地TTS语音"""
        if not voices:
            return None

        # 根据语言和性别选择语音
        language = self.supported_languages.get(
            request.voice_config_id or VoiceLanguage.ZH_CN, "zh-CN"
        )
        gender = request.gender or VoiceGender.FEMALE

        for voice in voices:
            voice_lang = voice.languages[0].split("-")[0] if voice.languages else ""
            if language.startswith(voice_lang):
                if gender == VoiceGender.FEMALE and "female" in voice.name.lower():
                    return voice
                elif gender == VoiceGender.MALE and "male" in voice.name.lower():
                    return voice

        # 如果没找到匹配的，返回第一个
        return voices[0]

    async def _get_audio_duration(self, audio_path: str) -> float:
        """获取音频时长"""
        try:
            import librosa

            y, sr = await asyncio.get_event_loop().run_in_executor(
                None, librosa.load, audio_path
            )

            return len(y) / sr

        except Exception:
            # 如果无法获取时长，返回0
            return 0.0

    async def get_available_voices(
        self, language: VoiceLanguage = VoiceLanguage.ZH_CN
    ) -> List[Dict[str, Any]]:
        """获取可用的语音列表"""
        try:
            if settings.TTS_ENGINE == "openai":
                return self._get_openai_voices()
            elif settings.TTS_ENGINE == "azure":
                return await self._get_azure_voices(language)
            elif settings.TTS_ENGINE == "google":
                return await self._get_google_voices(language)
            else:
                return self._get_local_voices()

        except Exception as e:
            return []

    def _get_openai_voices(self) -> List[Dict[str, Any]]:
        """获取OpenAI语音列表"""
        return [
            {"id": "alloy", "name": "Alloy", "gender": "neutral"},
            {"id": "echo", "name": "Echo", "gender": "male"},
            {"id": "fable", "name": "Fable", "gender": "male"},
            {"id": "onyx", "name": "Onyx", "gender": "male"},
            {"id": "nova", "name": "Nova", "gender": "female"},
            {"id": "shimmer", "name": "Shimmer", "gender": "female"},
        ]

    async def _get_azure_voices(self, language: VoiceLanguage) -> List[Dict[str, Any]]:
        """获取Azure语音列表"""
        # 这里应该调用Azure API获取语音列表
        # 为了简化，返回一些常用的语音
        return [
            {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓", "gender": "female"},
            {"id": "zh-CN-YunxiNeural", "name": "云希", "gender": "male"},
            {"id": "en-US-AriaNeural", "name": "Aria", "gender": "female"},
            {"id": "en-US-GuyNeural", "name": "Guy", "gender": "male"},
        ]

    async def _get_google_voices(self, language: VoiceLanguage) -> List[Dict[str, Any]]:
        """获取Google语音列表"""
        # 这里应该调用Google API获取语音列表
        return [
            {"id": "zh-CN-Wavenet-A", "name": "中文男声", "gender": "male"},
            {"id": "zh-CN-Wavenet-C", "name": "中文女声", "gender": "female"},
            {"id": "en-US-Wavenet-A", "name": "English Male", "gender": "male"},
            {"id": "en-US-Wavenet-C", "name": "English Female", "gender": "female"},
        ]

    def _get_local_voices(self) -> List[Dict[str, Any]]:
        """获取本地TTS语音列表"""
        try:
            import pyttsx3

            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            result = []
            for voice in voices:
                result.append(
                    {
                        "id": voice.id,
                        "name": voice.name,
                        "gender": "unknown",
                        "languages": voice.languages,
                    }
                )

            return result

        except Exception:
            return []


# 全局TTS服务实例
tts_service = TTSService()
