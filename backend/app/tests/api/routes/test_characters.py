import uuid
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.core.config import settings
from app.models.character import Character, CharacterTag
from app.models.user import User
from app.tests.utils.test_data_manager import TestDataManager


class TestCharacterAPI:
    """角色API测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data_manager(self, db: Session):
        """为每个测试方法设置数据管理器"""
        self.data_manager = TestDataManager(db)
        yield
        # 测试结束后清理数据
        self.data_manager.cleanup()

    def test_create_character_success(
        self, client: TestClient, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试成功创建角色"""
        character_data = {
            "name": "API测试角色",
            "short_bio": "这是一个通过API创建的测试角色",
            "persona_text": "你是一个API测试角色，用于测试系统功能。",
            "example_lines": ["你好，我是API测试角色", "很高兴通过API见到你"],
            "source": "API测试来源",
        }

        response = client.post(
            f"{settings.API_V1_STR}/characters/",
            json=character_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["name"] == character_data["name"]
        assert data["data"]["short_bio"] == character_data["short_bio"]
        assert data["data"]["persona_text"] == character_data["persona_text"]
        assert data["data"]["example_lines"] == character_data["example_lines"]
        assert data["data"]["source"] == character_data["source"]
        assert data["data"]["is_active"] is True
        assert "id" in data["data"]

    def test_create_character_duplicate_name(
        self, client: TestClient, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试创建重复名称的角色"""
        character_data = {
            "name": "重复名称测试",
            "short_bio": "测试重复名称",
            "persona_text": "测试角色",
        }

        # 第一次创建
        response1 = client.post(
            f"{settings.API_V1_STR}/characters/",
            json=character_data,
            headers=superuser_token_headers,
        )
        assert response1.status_code == 201

        # 第二次创建相同名称
        response2 = client.post(
            f"{settings.API_V1_STR}/characters/",
            json=character_data,
            headers=superuser_token_headers,
        )
        assert response2.status_code == 400
        assert "角色名称已存在" in response2.json()["msg"]

    def test_create_character_unauthorized(
        self, client: TestClient, normal_user_token_headers: Dict[str, str]
    ) -> None:
        """测试普通用户创建角色（应该失败）"""
        character_data = {
            "name": "未授权测试角色",
            "short_bio": "测试未授权创建",
            "persona_text": "测试角色",
        }

        response = client.post(
            f"{settings.API_V1_STR}/characters/",
            json=character_data,
            headers=normal_user_token_headers,
        )

        assert response.status_code == 403

    def test_get_characters(self, client: TestClient) -> None:
        """测试获取角色列表"""
        response = client.get(f"{settings.API_V1_STR}/characters/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data
        assert "characters" in data["data"]
        assert "total" in data["data"]
        assert isinstance(data["data"]["characters"], list)

    def test_get_characters_with_filters(self, client: TestClient, db: Session) -> None:
        """测试带过滤条件的角色列表"""
        # 创建测试角色
        from app.crud.character import character
        from app.models.character import CharacterCreate

        character_data = CharacterCreate(
            name="过滤测试角色",
            short_bio="用于测试过滤功能",
            persona_text="测试角色",
            is_active=True,
        )
        character.create(db, obj_in=character_data)

        # 测试过滤
        response = client.get(
            f"{settings.API_V1_STR}/characters/?is_active=true&limit=10"
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data["data"]

    def test_get_character_by_id(self, client: TestClient, db: Session) -> None:
        """测试根据ID获取角色"""
        # 创建测试角色
        from app.crud.character import character
        from app.models.character import CharacterCreate

        character_data = CharacterCreate(
            name="ID测试角色",
            short_bio="用于测试ID获取",
            persona_text="测试角色",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 获取角色
        response = client.get(f"{settings.API_V1_STR}/characters/{character_obj.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == str(character_obj.id)
        assert data["data"]["name"] == character_obj.name

    def test_get_character_not_found(self, client: TestClient) -> None:
        """测试获取不存在的角色"""
        fake_id = uuid.uuid4()
        response = client.get(f"{settings.API_V1_STR}/characters/{fake_id}")

        assert response.status_code == 404
        assert "角色未找到" in response.json()["msg"]

    def test_update_character(
        self, client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试更新角色"""
        # 创建测试角色
        from app.crud.character import character
        from app.models.character import CharacterCreate

        character_data = CharacterCreate(
            name="更新测试角色",
            short_bio="原始描述",
            persona_text="原始人格",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 更新角色
        update_data = {
            "short_bio": "更新后的描述",
            "persona_text": "更新后的人格",
        }

        response = client.put(
            f"{settings.API_V1_STR}/characters/{character_obj.id}",
            json=update_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["short_bio"] == update_data["short_bio"]
        assert data["data"]["persona_text"] == update_data["persona_text"]
        assert data["data"]["name"] == character_obj.name  # 未更新的字段保持不变

    def test_delete_character(
        self, client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试删除角色"""
        # 创建测试角色
        from app.crud.character import character
        from app.models.character import CharacterCreate

        character_data = CharacterCreate(
            name="删除测试角色",
            short_bio="用于测试删除",
            persona_text="测试角色",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 删除角色
        response = client.delete(
            f"{settings.API_V1_STR}/characters/{character_obj.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["is_active"] is False

    def test_search_characters(self, client: TestClient, db: Session) -> None:
        """测试搜索角色"""
        # 创建测试角色
        from app.crud.character import character
        from app.models.character import CharacterCreate

        character_data = CharacterCreate(
            name="搜索测试角色",
            short_bio="这是一个用于搜索测试的角色",
            persona_text="搜索测试人格",
        )
        character.create(db, obj_in=character_data)

        # 搜索角色
        response = client.get(
            f"{settings.API_V1_STR}/characters/search?query=搜索测试&search_type=text"
        )

        assert response.status_code == 200
        data = response.json()
        assert "results" in data["data"]
        assert "total" in data["data"]
        assert "query" in data["data"]
        assert "search_type" in data["data"]
        assert len(data["data"]["results"]) == 1
        assert data["data"]["results"][0]["character"]["name"] == "搜索测试角色"


class TestCharacterTagAPI:
    """角色标签API测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data_manager(self, db: Session):
        """为每个测试方法设置数据管理器"""
        self.data_manager = TestDataManager(db)
        yield
        # 测试结束后清理数据
        self.data_manager.cleanup()

    def test_create_character_tag_success(
        self, client: TestClient, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试成功创建标签"""
        tag_data = {
            "name": "API测试标签",
            "description": "这是一个通过API创建的测试标签",
            "color": "#FF0000",
        }

        response = client.post(
            f"{settings.API_V1_STR}/characters/tags/",
            json=tag_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["name"] == tag_data["name"]
        assert data["data"]["description"] == tag_data["description"]
        assert data["data"]["color"] == tag_data["color"]
        assert "id" in data["data"]

    def test_create_character_tag_duplicate_name(
        self, client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试创建重复名称的标签"""
        import uuid

        unique_name = f"重复标签测试_{uuid.uuid4().hex[:8]}"
        tag_data = {
            "name": unique_name,
            "description": "测试重复标签名称",
        }

        # 第一次创建
        response1 = client.post(
            f"{settings.API_V1_STR}/characters/tags/",
            json=tag_data,
            headers=superuser_token_headers,
        )
        assert response1.status_code == 201

        # 跟踪创建的标签以便清理
        tag_id = response1.json()["data"]["id"]
        from app.crud.character import character_tag

        tag_obj = character_tag.get(db, id=tag_id)
        if tag_obj:
            self.data_manager.track_tag(tag_obj)

        # 第二次创建相同名称
        response2 = client.post(
            f"{settings.API_V1_STR}/characters/tags/",
            json=tag_data,
            headers=superuser_token_headers,
        )
        assert response2.status_code == 400
        assert "标签名称已存在" in response2.json()["msg"]

    def test_get_character_tags(self, client: TestClient) -> None:
        """测试获取标签列表"""
        response = client.get(f"{settings.API_V1_STR}/characters/tags/")

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "total" in data["data"]
        assert isinstance(data["data"]["tags"], list)

    def test_get_character_tag_by_id(self, client: TestClient, db: Session) -> None:
        """测试根据ID获取标签"""
        # 创建测试标签
        from app.crud.character import character_tag
        from app.models.character import CharacterTagCreate

        tag_data = CharacterTagCreate(
            name="ID测试标签",
            description="用于测试ID获取",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 获取标签
        response = client.get(f"{settings.API_V1_STR}/characters/tags/{tag_obj.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == str(tag_obj.id)
        assert data["data"]["name"] == tag_obj.name

    def test_update_character_tag(
        self, client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试更新标签"""
        # 创建测试标签
        from app.crud.character import character_tag
        from app.models.character import CharacterTagCreate

        tag_data = CharacterTagCreate(
            name="更新测试标签",
            description="原始描述",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 更新标签
        update_data = {
            "description": "更新后的描述",
            "color": "#00FF00",
        }

        response = client.put(
            f"{settings.API_V1_STR}/characters/tags/{tag_obj.id}",
            json=update_data,
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["description"] == update_data["description"]
        assert data["data"]["color"] == update_data["color"]
        assert data["data"]["name"] == tag_obj.name  # 未更新的字段保持不变

    def test_delete_character_tag(
        self, client: TestClient, db: Session, superuser_token_headers: Dict[str, str]
    ) -> None:
        """测试删除标签"""
        # 创建测试标签
        from app.crud.character import character_tag
        from app.models.character import CharacterTagCreate

        tag_data = CharacterTagCreate(
            name="删除测试标签",
            description="用于测试删除",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 删除标签
        response = client.delete(
            f"{settings.API_V1_STR}/characters/tags/{tag_obj.id}",
            headers=superuser_token_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == tag_obj.name
