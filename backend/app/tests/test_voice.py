import pytest
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.voice import (
    VoiceMessage,
    VoiceMessageCreate,
    VoiceConfig,
    VoiceConfigCreate,
    AudioProcessingTask,
    AudioProcessingTaskCreate,
    VoiceMessageType,
    AudioFormat,
    AudioQuality,
    VoiceLanguage,
    VoiceGender,
    VoiceEmotion,
    AudioProcessingStatus,
)
from app.crud.voice import voice_crud
from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.audio_storage_service import audio_storage_service


class TestVoiceMessageCRUD:
    """语音消息CRUD测试"""

    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.fixture
    def sample_voice_message_data(self):
        return {
            "message_id": uuid.uuid4(),
            "voice_type": VoiceMessageType.USER_INPUT,
            "audio_url": "https://example.com/audio.mp3",
            "audio_format": AudioFormat.MP3,
            "audio_quality": AudioQuality.MEDIUM,
            "duration": 5.5,
            "file_size": 1024000,
            "language": VoiceLanguage.ZH_CN,
            "gender": VoiceGender.FEMALE,
            "emotion": VoiceEmotion.NEUTRAL,
            "processing_status": AudioProcessingStatus.COMPLETED,
            "transcription": "这是一个测试语音消息",
            "confidence_score": 0.95,
        }

    def test_create_voice_message(self, mock_db, sample_voice_message_data):
        """测试创建语音消息"""
        # 准备测试数据
        voice_message_create = VoiceMessageCreate(**sample_voice_message_data)

        # 模拟数据库操作
        mock_voice_message = VoiceMessage(**sample_voice_message_data)
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()
        mock_db.refresh = MagicMock(
            side_effect=lambda obj: setattr(obj, "id", uuid.uuid4())
        )

        # 执行创建
        result = voice_crud.create(mock_db, obj_in=voice_message_create)

        # 验证结果
        assert result is not None
        assert result.message_id == sample_voice_message_data["message_id"]
        assert result.voice_type == sample_voice_message_data["voice_type"]
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    def test_get_voice_message(self, mock_db):
        """测试获取语音消息"""
        # 准备测试数据
        message_id = uuid.uuid4()
        mock_voice_message = VoiceMessage(
            id=message_id,
            message_id=uuid.uuid4(),
            voice_type=VoiceMessageType.USER_INPUT,
            audio_url="https://example.com/audio.mp3",
            audio_format=AudioFormat.MP3,
            audio_quality=AudioQuality.MEDIUM,
            duration=5.5,
            file_size=1024000,
            language=VoiceLanguage.ZH_CN,
            processing_status=AudioProcessingStatus.COMPLETED,
        )

        # 模拟数据库查询
        mock_db.get.return_value = mock_voice_message

        # 执行查询
        result = voice_crud.get(mock_db, id=message_id)

        # 验证结果
        assert result is not None
        assert result.id == message_id
        mock_db.get.assert_called_once_with(VoiceMessage, message_id)

    def test_get_voice_messages_with_filters(self, mock_db):
        """测试获取语音消息列表（带过滤器）"""
        # 准备测试数据
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 模拟数据库查询结果
        mock_voice_messages = [
            VoiceMessage(
                id=uuid.uuid4(),
                message_id=uuid.uuid4(),
                voice_type=VoiceMessageType.USER_INPUT,
                audio_url="https://example.com/audio1.mp3",
                audio_format=AudioFormat.MP3,
                audio_quality=AudioQuality.MEDIUM,
                duration=5.5,
                file_size=1024000,
                language=VoiceLanguage.ZH_CN,
                processing_status=AudioProcessingStatus.COMPLETED,
            ),
            VoiceMessage(
                id=uuid.uuid4(),
                message_id=uuid.uuid4(),
                voice_type=VoiceMessageType.USER_INPUT,
                audio_url="https://example.com/audio2.mp3",
                audio_format=AudioFormat.MP3,
                audio_quality=AudioQuality.HIGH,
                duration=3.2,
                file_size=800000,
                language=VoiceLanguage.ZH_CN,
                processing_status=AudioProcessingStatus.COMPLETED,
            ),
        ]

        # 模拟数据库查询
        mock_query = MagicMock()
        mock_query.where.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_voice_messages

        mock_count_query = MagicMock()
        mock_count_query.select_from.return_value = mock_count_query
        mock_count_query.one.return_value = 2

        mock_db.exec.side_effect = [mock_count_query, mock_query]

        # 执行查询
        filters = {"conversation_id": conversation_id, "language": VoiceLanguage.ZH_CN}
        result, total = voice_crud.get_multi(
            mock_db, skip=0, limit=10, filters=filters, user_id=user_id
        )

        # 验证结果
        assert len(result) == 2
        assert total == 2
        assert all(msg.conversation_id == conversation_id for msg in result)


class TestSTTService:
    """语音转文本服务测试"""

    @pytest.fixture
    def mock_audio_file(self):
        return "/tmp/test_audio.wav"

    @pytest.mark.asyncio
    async def test_transcribe_audio(self, mock_audio_file):
        """测试音频转录"""
        # 模拟文件存在
        with patch("os.path.exists", return_value=True):
            # 模拟librosa加载
            with patch("librosa.load") as mock_load:
                mock_load.return_value = (None, 16000)  # 模拟音频数据

                # 执行转录
                result = await stt_service.transcribe_audio(
                    mock_audio_file,
                    language=VoiceLanguage.ZH_CN,
                    enable_auto_detection=False,
                    enable_punctuation=True,
                    enable_word_timestamps=False,
                )

                # 验证结果
                assert result is not None
                assert result.text is not None
                assert result.confidence is not None
                assert result.language == VoiceLanguage.ZH_CN
                assert result.duration is not None
                assert result.word_count is not None

    @pytest.mark.asyncio
    async def test_validate_audio_quality(self, mock_audio_file):
        """测试音频质量验证"""
        # 模拟文件存在
        with patch("os.path.exists", return_value=True):
            # 模拟librosa加载
            with patch("librosa.load") as mock_load:
                import numpy as np

                mock_load.return_value = (
                    np.random.random(16000),
                    16000,
                )  # 模拟音频数据

                # 执行质量验证
                result = await stt_service.validate_audio_quality(mock_audio_file)

                # 验证结果
                assert result is not None
                assert "quality_score" in result
                assert "duration" in result
                assert "sample_rate" in result
                assert "rms" in result
                assert "zero_crossing_rate" in result
                assert "issues" in result
                assert "is_good_quality" in result

    @pytest.mark.asyncio
    async def test_file_not_found(self):
        """测试文件不存在的情况"""
        with patch("os.path.exists", return_value=False):
            with pytest.raises(Exception, match="语音识别失败"):
                await stt_service.transcribe_audio("/nonexistent/file.wav")


class TestTTSService:
    """文本转语音服务测试"""

    @pytest.fixture
    def sample_synthesis_request(self):
        from app.models.voice import VoiceSynthesisRequest

        return VoiceSynthesisRequest(
            text="这是一个测试文本",
            language=VoiceLanguage.ZH_CN,
            gender=VoiceGender.FEMALE,
            emotion=VoiceEmotion.NEUTRAL,
            speed=1.0,
            pitch=1.0,
            volume=1.0,
            output_format=AudioFormat.MP3,
            output_quality=AudioQuality.MEDIUM,
            voice_config_id=None,
        )

    @pytest.mark.asyncio
    async def test_synthesize_speech(self, sample_synthesis_request):
        """测试语音合成"""
        # 模拟TTS引擎
        with patch("openai.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client

            # 模拟API响应
            mock_response = MagicMock()
            mock_response.content = b"fake_audio_content"
            mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

            # 执行合成
            result = await tts_service.synthesize_speech(sample_synthesis_request)

            # 验证结果
            assert result is not None
            assert result.audio_url is not None
            assert result.duration is not None
            assert result.file_size is not None
            assert result.format == sample_synthesis_request.output_format
            assert result.quality == sample_synthesis_request.output_quality

    @pytest.mark.asyncio
    async def test_get_available_voices(self):
        """测试获取可用语音列表"""
        voices = await tts_service.get_available_voices(VoiceLanguage.ZH_CN)

        # 验证结果
        assert isinstance(voices, list)
        if voices:  # 如果有语音可用
            for voice in voices:
                assert "id" in voice
                assert "name" in voice
                assert "gender" in voice

    def test_empty_text_validation(self):
        """测试空文本验证"""
        from app.models.voice import VoiceSynthesisRequest

        with pytest.raises(ValueError):
            VoiceSynthesisRequest(
                text="",  # 空文本
                language=VoiceLanguage.ZH_CN,
                output_format=AudioFormat.MP3,
                output_quality=AudioQuality.MEDIUM,
                voice_config_id=None,
            )

    def test_text_length_validation(self):
        """测试文本长度验证"""
        from app.models.voice import VoiceSynthesisRequest

        long_text = "a" * 5001  # 超过5000字符

        with pytest.raises(ValueError):
            VoiceSynthesisRequest(
                text=long_text,
                language=VoiceLanguage.ZH_CN,
                output_format=AudioFormat.MP3,
                output_quality=AudioQuality.MEDIUM,
                voice_config_id=None,
            )


class TestAudioStorageService:
    """音频存储服务测试"""

    @pytest.fixture
    def mock_storage_service(self):
        return audio_storage_service

    @pytest.mark.asyncio
    async def test_save_uploaded_file(self, mock_storage_service):
        """测试保存上传文件"""
        # 准备测试数据
        file_content = b"fake_audio_content"
        filename = "test_audio.mp3"
        content_type = "audio/mpeg"
        user_id = uuid.uuid4()
        conversation_id = uuid.uuid4()

        # 执行保存
        result = await mock_storage_service.save_uploaded_file(
            file_content=file_content,
            filename=filename,
            content_type=content_type,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        # 验证结果
        assert result is not None
        assert "file_id" in result
        assert "original_filename" in result
        assert "storage_path" in result
        assert "file_size" in result
        assert "audio_format" in result
        assert result["original_filename"] == filename
        assert result["file_size"] == len(file_content)

    @pytest.mark.asyncio
    async def test_get_file(self, mock_storage_service):
        """测试获取文件信息"""
        # 先保存一个文件
        file_content = b"fake_audio_content"
        filename = "test_audio.mp3"
        content_type = "audio/mpeg"
        user_id = uuid.uuid4()

        save_result = await mock_storage_service.save_uploaded_file(
            file_content=file_content,
            filename=filename,
            content_type=content_type,
            user_id=user_id,
        )

        # 获取文件信息
        file_info = await mock_storage_service.get_file(save_result["file_id"])

        # 验证结果
        assert file_info is not None
        assert file_info["file_id"] == save_result["file_id"]
        assert file_info["original_filename"] == filename
        assert file_info["file_size"] == len(file_content)

    @pytest.mark.asyncio
    async def test_delete_file(self, mock_storage_service):
        """测试删除文件"""
        # 先保存一个文件
        file_content = b"fake_audio_content"
        filename = "test_audio.mp3"
        content_type = "audio/mpeg"
        user_id = uuid.uuid4()

        save_result = await mock_storage_service.save_uploaded_file(
            file_content=file_content,
            filename=filename,
            content_type=content_type,
            user_id=user_id,
        )

        # 删除文件
        delete_result = await mock_storage_service.delete_file(save_result["file_id"])

        # 验证结果
        assert delete_result is True

        # 验证文件已被删除
        file_info = await mock_storage_service.get_file(save_result["file_id"])
        assert file_info is None


class TestVoiceWebSocket:
    """语音WebSocket测试"""

    @pytest.fixture
    def mock_websocket(self):
        websocket = AsyncMock()
        websocket.send_text = AsyncMock()
        websocket.receive_text = AsyncMock()
        websocket.close = AsyncMock()
        return websocket

    @pytest.mark.asyncio
    async def test_voice_upload_start_message(self, mock_websocket):
        """测试语音上传开始消息处理"""
        from app.api.routes.voice_websocket import handle_voice_upload_start

        # 准备测试数据
        data = {
            "file_id": "test_file_123",
            "filename": "test_audio.mp3",
            "file_size": 1024000,
        }

        # 执行处理
        await handle_voice_upload_start(mock_websocket, "test_connection", data)

        # 验证WebSocket消息发送
        assert mock_websocket.send_text.called

    @pytest.mark.asyncio
    async def test_voice_processing_start_message(self, mock_websocket):
        """测试语音处理开始消息处理"""
        from app.api.routes.voice_websocket import handle_voice_processing_start

        # 准备测试数据
        data = {"file_id": "test_file_123", "processing_type": "transcription"}

        # 执行处理
        await handle_voice_processing_start(mock_websocket, "test_connection", data)

        # 验证WebSocket消息发送
        assert mock_websocket.send_text.called

    @pytest.mark.asyncio
    async def test_voice_synthesis_start_message(self, mock_websocket):
        """测试语音合成开始消息处理"""
        from app.api.routes.voice_websocket import handle_voice_synthesis_start

        # 准备测试数据
        data = {"text": "这是一个测试文本", "voice_config_id": str(uuid.uuid4())}

        # 执行处理
        await handle_voice_synthesis_start(mock_websocket, "test_connection", data)

        # 验证WebSocket消息发送
        assert mock_websocket.send_text.called

    @pytest.mark.asyncio
    async def test_error_handling(self, mock_websocket):
        """测试错误处理"""
        from app.api.routes.voice_websocket import handle_voice_upload_start

        # 准备无效数据
        data = {}  # 缺少必要字段

        # 执行处理
        await handle_voice_upload_start(mock_websocket, "test_connection", data)

        # 验证错误消息发送
        assert mock_websocket.send_text.called


class TestVoiceIntegration:
    """语音功能集成测试"""

    @pytest.mark.asyncio
    async def test_voice_message_workflow(self):
        """测试语音消息完整工作流"""
        # 1. 创建语音消息
        voice_message_data = {
            "message_id": uuid.uuid4(),
            "voice_type": VoiceMessageType.USER_INPUT,
            "audio_url": "https://example.com/audio.mp3",
            "audio_format": AudioFormat.MP3,
            "audio_quality": AudioQuality.MEDIUM,
            "duration": 5.5,
            "file_size": 1024000,
            "language": VoiceLanguage.ZH_CN,
            "processing_status": AudioProcessingStatus.PENDING,
        }

        voice_message = VoiceMessageCreate(**voice_message_data)

        # 2. 模拟语音识别
        with patch("os.path.exists", return_value=True):
            with patch("librosa.load") as mock_load:
                mock_load.return_value = (None, 16000)

                transcription_result = await stt_service.transcribe_audio(
                    "/tmp/test_audio.wav", language=VoiceLanguage.ZH_CN
                )

                assert transcription_result is not None
                assert transcription_result.text is not None

        # 3. 模拟语音合成
        from app.models.voice import VoiceSynthesisRequest

        synthesis_request = VoiceSynthesisRequest(
            text="这是合成的语音文本",
            language=VoiceLanguage.ZH_CN,
            output_format=AudioFormat.MP3,
            output_quality=AudioQuality.MEDIUM,
        )

        with patch("openai.AsyncOpenAI") as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            mock_response = MagicMock()
            mock_response.content = b"fake_audio_content"
            mock_client.audio.speech.create = AsyncMock(return_value=mock_response)

            synthesis_result = await tts_service.synthesize_speech(synthesis_request)

            assert synthesis_result is not None
            assert synthesis_result.audio_url is not None

    @pytest.mark.asyncio
    async def test_voice_quality_workflow(self):
        """测试语音质量检测工作流"""
        # 模拟音频文件
        with patch("os.path.exists", return_value=True):
            with patch("librosa.load") as mock_load:
                import numpy as np

                mock_load.return_value = (np.random.random(16000), 16000)

                # 执行质量检测
                quality_result = await stt_service.validate_audio_quality(
                    "/tmp/test_audio.wav"
                )

                # 验证结果
                assert quality_result is not None
                assert "quality_score" in quality_result
                assert "issues" in quality_result
                assert "recommendations" in quality_result
                assert "is_good_quality" in quality_result
