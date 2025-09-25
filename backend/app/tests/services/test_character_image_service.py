"""
角色形象图片生成服务测试
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from app.services.character_image_service import CharacterImageService
from app.models.character import Character


class TestCharacterImageService:
    """角色形象图片生成服务测试类"""

    @pytest.fixture
    def character_image_service(self):
        """创建服务实例"""
        return CharacterImageService()

    @pytest.fixture
    def mock_character(self):
        """创建模拟角色"""
        character = Character(
            id=uuid4(),
            name="测试角色",
            short_bio="这是一个测试角色",
            persona_text="你是一个测试角色，用于测试AI图片生成功能。",
            example_lines=["你好，我是测试角色"],
            source="测试来源",
            is_active=True,
            auto_generate_image=True,
            image_style="realistic",
            image_size="1024x1024",
        )
        return character

    def test_build_image_prompt_realistic(
        self, character_image_service, mock_character
    ):
        """测试构建写实风格提示词"""
        prompt = character_image_service._build_image_prompt(
            mock_character, "realistic"
        )

        assert "realistic portrait of 测试角色" in prompt
        assert "这是一个测试角色" in prompt
        assert "photorealistic, detailed, professional photography" in prompt
        assert "high quality, detailed, well-lit, centered composition" in prompt

    def test_build_image_prompt_anime(self, character_image_service, mock_character):
        """测试构建动漫风格提示词"""
        prompt = character_image_service._build_image_prompt(mock_character, "anime")

        assert "anime portrait of 测试角色" in prompt
        assert "anime style, manga art, colorful, detailed" in prompt

    def test_build_image_prompt_cartoon(self, character_image_service, mock_character):
        """测试构建卡通风格提示词"""
        prompt = character_image_service._build_image_prompt(mock_character, "cartoon")

        assert "cartoon portrait of 测试角色" in prompt
        assert "cartoon style, colorful, friendly, detailed" in prompt

    def test_build_image_prompt_artistic(self, character_image_service, mock_character):
        """测试构建艺术风格提示词"""
        prompt = character_image_service._build_image_prompt(mock_character, "artistic")

        assert "artistic portrait of 测试角色" in prompt
        assert "artistic painting, detailed, beautiful, creative" in prompt

    def test_extract_persona_keywords(self, character_image_service):
        """测试从人格文本中提取关键词"""
        persona_text = "你是一个年轻的男性医生，身材高大，穿着正式的白色大褂。"
        keywords = character_image_service._extract_persona_keywords(persona_text)

        assert "young" in keywords
        assert "male" in keywords
        assert "doctor" in keywords
        assert "tall" in keywords
        assert "formal" in keywords

    def test_extract_persona_keywords_empty(self, character_image_service):
        """测试空人格文本的关键词提取"""
        keywords = character_image_service._extract_persona_keywords("")
        assert keywords == ""

    def test_get_supported_styles(self, character_image_service):
        """测试获取支持的风格"""
        styles = character_image_service.get_supported_styles()

        assert "realistic" in styles
        assert "anime" in styles
        assert "cartoon" in styles
        assert "artistic" in styles
        assert styles["realistic"] == "写实风格"
        assert styles["anime"] == "动漫风格"

    def test_get_supported_sizes(self, character_image_service):
        """测试获取支持的尺寸"""
        sizes = character_image_service.get_supported_sizes()

        assert "1024x1024" in sizes
        assert "1792x1024" in sizes
        assert "1024x1792" in sizes
        assert sizes["1024x1024"] == "正方形 (1024x1024)"

    @pytest.mark.asyncio
    async def test_call_dalle_api_success(self, character_image_service):
        """测试DALL-E API调用成功"""
        mock_response_data = {
            "data": [{"url": "https://example.com/generated-image.jpg"}]
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await character_image_service._call_dalle_api(
                "test prompt", "1024x1024"
            )

            assert result == "https://example.com/generated-image.jpg"

    @pytest.mark.asyncio
    async def test_call_dalle_api_failure(self, character_image_service):
        """测试DALL-E API调用失败"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad Request"

            mock_client.return_value.__aenter__.return_value.post.return_value = (
                mock_response
            )

            result = await character_image_service._call_dalle_api(
                "test prompt", "1024x1024"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_call_dalle_api_exception(self, character_image_service):
        """测试DALL-E API调用异常"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.post.side_effect = (
                Exception("Network error")
            )

            result = await character_image_service._call_dalle_api(
                "test prompt", "1024x1024"
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_generate_character_image_success(
        self, character_image_service, mock_character
    ):
        """测试成功生成角色形象图片"""
        with patch.object(
            character_image_service,
            "_call_dalle_api",
            return_value="https://example.com/image.jpg",
        ):
            result = await character_image_service.generate_character_image(
                mock_character
            )

            assert result == "https://example.com/image.jpg"

    @pytest.mark.asyncio
    async def test_generate_character_image_failure(
        self, character_image_service, mock_character
    ):
        """测试生成角色形象图片失败"""
        with patch.object(
            character_image_service, "_call_dalle_api", return_value=None
        ):
            result = await character_image_service.generate_character_image(
                mock_character
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_generate_character_image_exception(
        self, character_image_service, mock_character
    ):
        """测试生成角色形象图片异常"""
        with patch.object(
            character_image_service,
            "_call_dalle_api",
            side_effect=Exception("API error"),
        ):
            result = await character_image_service.generate_character_image(
                mock_character
            )

            assert result is None

    @pytest.mark.asyncio
    async def test_validate_image_url_success(self, character_image_service):
        """测试验证图片URL成功"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200

            mock_client.return_value.__aenter__.return_value.head.return_value = (
                mock_response
            )

            result = await character_image_service.validate_image_url(
                "https://example.com/image.jpg"
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_validate_image_url_failure(self, character_image_service):
        """测试验证图片URL失败"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_client.return_value.__aenter__.return_value.head.return_value = (
                mock_response
            )

            result = await character_image_service.validate_image_url(
                "https://example.com/image.jpg"
            )

            assert result is False

    @pytest.mark.asyncio
    async def test_download_and_validate_image_success(self, character_image_service):
        """测试下载并验证图片成功"""
        # 创建一个简单的测试图片
        from PIL import Image
        import io

        test_image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        test_image.save(image_bytes, format="JPEG")
        image_data = image_bytes.getvalue()

        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = image_data

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await character_image_service.download_and_validate_image(
                "https://example.com/image.jpg"
            )

            assert result == image_data

    @pytest.mark.asyncio
    async def test_download_and_validate_image_invalid(self, character_image_service):
        """测试下载并验证无效图片"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"invalid image data"

            mock_client.return_value.__aenter__.return_value.get.return_value = (
                mock_response
            )

            result = await character_image_service.download_and_validate_image(
                "https://example.com/image.jpg"
            )

            assert result is None
