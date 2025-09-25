"""
角色AI图片生成API测试
"""

import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app
from app.models.character import Character
from app.tests.utils.test_data_manager import TestDataManager


class TestCharacterImageAPI:
    """角色AI图片生成API测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data_manager(self, db: Session):
        """为每个测试方法设置数据管理器"""
        self.data_manager = TestDataManager(db)
        yield
        # 测试结束后清理数据
        self.data_manager.cleanup()

    def test_generate_character_image_success(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试成功生成角色AI形象图片"""
        # 创建测试角色
        character = self.data_manager.create_test_character(
            name="AI图片测试角色",
            short_bio="用于测试AI图片生成的角色",
            persona_text="你是一个测试角色，用于测试AI图片生成功能。",
            auto_generate_image=True,
            image_style="realistic",
            image_size="1024x1024",
        )

        with patch(
            "app.services.character_image_service.character_image_service.generate_character_image"
        ) as mock_generate:
            mock_generate.return_value = "https://example.com/generated-image.jpg"

            response = client.post(
                f"/api/v1/characters/{character.id}/generate-image",
                params={"style": "realistic", "size": "1024x1024"},
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["character_id"] == str(character.id)
            assert (
                data["data"]["avatar_url"] == "https://example.com/generated-image.jpg"
            )
            assert data["data"]["style"] == "realistic"
            assert data["data"]["size"] == "1024x1024"

    def test_generate_character_image_character_not_found(
        self, client: TestClient, superuser_token_headers: dict
    ):
        """测试角色不存在时的AI图片生成"""
        fake_character_id = uuid4()

        response = client.post(
            f"/api/v1/characters/{fake_character_id}/generate-image",
            params={"style": "realistic", "size": "1024x1024"},
            headers=superuser_token_headers,
        )

        assert response.status_code == 404
        data = response.json()
        assert "角色未找到" in data["detail"]

    def test_generate_character_image_api_failure(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试AI图片生成API失败"""
        character = self.data_manager.create_test_character(
            name="AI图片失败测试角色", short_bio="用于测试AI图片生成失败的角色"
        )

        with patch(
            "app.services.character_image_service.character_image_service.generate_character_image"
        ) as mock_generate:
            mock_generate.return_value = None

            response = client.post(
                f"/api/v1/characters/{character.id}/generate-image",
                params={"style": "realistic", "size": "1024x1024"},
                headers=superuser_token_headers,
            )

            assert response.status_code == 500
            data = response.json()
            assert "AI形象图片生成失败" in data["detail"]

    def test_generate_character_image_api_exception(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试AI图片生成API异常"""
        character = self.data_manager.create_test_character(
            name="AI图片异常测试角色", short_bio="用于测试AI图片生成异常的角色"
        )

        with patch(
            "app.services.character_image_service.character_image_service.generate_character_image"
        ) as mock_generate:
            mock_generate.side_effect = Exception("API调用异常")

            response = client.post(
                f"/api/v1/characters/{character.id}/generate-image",
                params={"style": "realistic", "size": "1024x1024"},
                headers=superuser_token_headers,
            )

            assert response.status_code == 500
            data = response.json()
            assert "生成AI形象图片失败" in data["detail"]

    def test_get_image_generation_styles(self, client: TestClient):
        """测试获取支持的AI图片生成风格"""
        response = client.get("/api/v1/characters/image-generation/styles")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "realistic" in data["data"]
        assert "anime" in data["data"]
        assert "cartoon" in data["data"]
        assert "artistic" in data["data"]

    def test_get_image_generation_sizes(self, client: TestClient):
        """测试获取支持的AI图片生成尺寸"""
        response = client.get("/api/v1/characters/image-generation/sizes")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "1024x1024" in data["data"]
        assert "1792x1024" in data["data"]
        assert "1024x1792" in data["data"]

    def test_validate_character_image_success(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试验证角色头像图片成功"""
        character = self.data_manager.create_test_character(
            name="图片验证测试角色",
            short_bio="用于测试图片验证的角色",
            avatar_url="https://example.com/valid-image.jpg",
        )

        with patch(
            "app.services.character_image_service.character_image_service.validate_image_url"
        ) as mock_validate:
            mock_validate.return_value = True

            response = client.post(
                f"/api/v1/characters/{character.id}/validate-image",
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["character_id"] == str(character.id)
            assert data["data"]["avatar_url"] == "https://example.com/valid-image.jpg"
            assert data["data"]["is_valid"] is True

    def test_validate_character_image_no_avatar(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试验证没有头像的角色"""
        character = self.data_manager.create_test_character(
            name="无头像测试角色", short_bio="没有头像的角色"
        )

        response = client.post(
            f"/api/v1/characters/{character.id}/validate-image",
            headers=superuser_token_headers,
        )

        assert response.status_code == 400
        data = response.json()
        assert "角色没有头像图片" in data["detail"]

    def test_validate_character_image_invalid(
        self, client: TestClient, superuser_token_headers: dict, db: Session
    ):
        """测试验证无效的角色头像图片"""
        character = self.data_manager.create_test_character(
            name="无效图片测试角色",
            short_bio="用于测试无效图片验证的角色",
            avatar_url="https://example.com/invalid-image.jpg",
        )

        with patch(
            "app.services.character_image_service.character_image_service.validate_image_url"
        ) as mock_validate:
            mock_validate.return_value = False

            response = client.post(
                f"/api/v1/characters/{character.id}/validate-image",
                headers=superuser_token_headers,
            )

            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["is_valid"] is False

    def test_create_character_with_auto_generate_image(
        self, client: TestClient, superuser_token_headers: dict
    ):
        """测试创建角色时自动生成AI图片"""
        character_data = {
            "name": "自动生成图片测试角色",
            "short_bio": "创建时自动生成AI图片的角色",
            "persona_text": "你是一个测试角色，用于测试自动生成AI图片功能。",
            "example_lines": ["你好，我是自动生成图片的测试角色"],
            "source": "测试来源",
            "auto_generate_image": True,
            "image_style": "realistic",
            "image_size": "1024x1024",
        }

        with patch(
            "app.services.character_image_service.character_image_service.generate_character_image"
        ) as mock_generate:
            mock_generate.return_value = "https://example.com/auto-generated-image.jpg"

            response = client.post(
                "/api/v1/characters/",
                json=character_data,
                headers=superuser_token_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["name"] == character_data["name"]
            assert data["data"]["auto_generate_image"] is True
            assert (
                data["data"]["avatar_url"]
                == "https://example.com/auto-generated-image.jpg"
            )

    def test_create_character_with_existing_avatar_no_auto_generate(
        self, client: TestClient, superuser_token_headers: dict
    ):
        """测试创建角色时已有头像不自动生成AI图片"""
        character_data = {
            "name": "已有头像测试角色",
            "short_bio": "已有头像的角色",
            "persona_text": "你是一个测试角色，已有头像。",
            "example_lines": ["你好，我是已有头像的测试角色"],
            "source": "测试来源",
            "avatar_url": "https://example.com/existing-image.jpg",
            "auto_generate_image": True,
            "image_style": "realistic",
            "image_size": "1024x1024",
        }

        with patch(
            "app.services.character_image_service.character_image_service.generate_character_image"
        ) as mock_generate:
            response = client.post(
                "/api/v1/characters/",
                json=character_data,
                headers=superuser_token_headers,
            )

            assert response.status_code == 201
            data = response.json()
            assert data["code"] == 0
            assert (
                data["data"]["avatar_url"] == "https://example.com/existing-image.jpg"
            )

            # 验证没有调用AI图片生成
            mock_generate.assert_not_called()

    def test_unauthorized_access(self, client: TestClient, db: Session):
        """测试未授权访问"""
        character = self.data_manager.create_test_character(
            name="未授权测试角色", short_bio="用于测试未授权访问的角色"
        )

        # 测试生成AI图片
        response = client.post(
            f"/api/v1/characters/{character.id}/generate-image",
            params={"style": "realistic", "size": "1024x1024"},
        )
        assert response.status_code == 401

        # 测试验证图片
        response = client.post(f"/api/v1/characters/{character.id}/validate-image")
        assert response.status_code == 401
