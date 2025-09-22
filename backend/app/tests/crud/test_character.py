import uuid
from typing import List

import pytest
from sqlmodel import Session

from app.crud.character import character, character_tag
from app.models.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    CharacterTag,
    CharacterTagCreate,
    CharacterTagUpdate,
)
from app.tests.utils.test_data_manager import TestDataManager


class TestCharacterCRUD:
    """角色CRUD测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data_manager(self, db: Session):
        """为每个测试方法设置数据管理器"""
        self.data_manager = TestDataManager(db)
        yield
        # 测试结束后清理数据
        self.data_manager.cleanup()

    def test_create_character(self, db: Session) -> None:
        """测试创建角色"""
        character_data = CharacterCreate(
            name="测试角色",
            short_bio="这是一个测试角色",
            persona_text="你是一个测试角色，用于测试系统功能。",
            example_lines=["你好，我是测试角色", "很高兴见到你"],
            source="测试来源",
        )

        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        assert character_obj.name == character_data.name
        assert character_obj.short_bio == character_data.short_bio
        assert character_obj.persona_text == character_data.persona_text
        assert character_obj.example_lines == character_data.example_lines
        assert character_obj.source == character_data.source
        assert character_obj.is_active is True
        assert character_obj.id is not None

    def test_get_character(self, db: Session) -> None:
        """测试获取角色"""
        # 创建测试角色
        character_data = CharacterCreate(
            name="获取测试角色",
            short_bio="用于测试获取功能",
            persona_text="测试角色",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 获取角色
        retrieved_character = character.get(db, id=character_obj.id)

        assert retrieved_character is not None
        assert retrieved_character.id == character_obj.id
        assert retrieved_character.name == character_obj.name

    def test_get_character_not_found(self, db: Session) -> None:
        """测试获取不存在的角色"""
        fake_id = uuid.uuid4()
        retrieved_character = character.get(db, id=fake_id)

        assert retrieved_character is None

    def test_get_character_by_name(self, db: Session) -> None:
        """测试根据名称获取角色"""
        # 使用唯一的名称避免冲突
        unique_name = f"名称测试角色_{uuid.uuid4().hex[:8]}"
        character_data = CharacterCreate(
            name=unique_name,
            short_bio="用于测试名称获取",
            persona_text="测试角色",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        retrieved_character = character.get_by_name(db, name=character_obj.name)

        assert retrieved_character is not None
        assert retrieved_character.id == character_obj.id
        assert retrieved_character.name == character_obj.name

    def test_get_multi_characters(self, db: Session) -> None:
        """测试获取多个角色"""
        # 先获取当前总数
        _, initial_total = character.get_multi(db, skip=0, limit=1000)

        # 创建多个测试角色
        for i in range(3):
            character_data = CharacterCreate(
                name=f"多角色测试{i}",
                short_bio=f"多角色测试描述{i}",
                persona_text=f"测试角色{i}",
            )
            character.create(db, obj_in=character_data)

        characters, total = character.get_multi(db, skip=0, limit=10)

        assert len(characters) >= 3
        assert total == initial_total + 3

    def test_update_character(self, db: Session) -> None:
        """测试更新角色"""
        # 创建测试角色
        character_data = CharacterCreate(
            name="更新测试角色",
            short_bio="原始描述",
            persona_text="原始人格",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 更新角色
        update_data = CharacterUpdate(
            short_bio="更新后的描述",
            persona_text="更新后的人格",
        )
        updated_character = character.update(
            db, db_obj=character_obj, obj_in=update_data
        )

        assert updated_character.short_bio == update_data.short_bio
        assert updated_character.persona_text == update_data.persona_text
        assert updated_character.name == character_obj.name  # 未更新的字段保持不变

    def test_delete_character(self, db: Session) -> None:
        """测试删除角色（软删除）"""
        # 创建测试角色
        character_data = CharacterCreate(
            name="删除测试角色",
            short_bio="用于测试删除",
            persona_text="测试角色",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 删除角色
        deleted_character = character.delete(db, id=character_obj.id)

        assert deleted_character is not None
        assert deleted_character.is_active is False

    def test_search_characters(self, db: Session) -> None:
        """测试搜索角色"""
        # 使用唯一的名称和搜索词避免冲突
        unique_suffix = uuid.uuid4().hex[:8]
        unique_name = f"搜索测试角色_{unique_suffix}"
        
        character_data = CharacterCreate(
            name=unique_name,
            short_bio=f"这是一个用于搜索测试的角色_{unique_suffix}",
            persona_text=f"搜索测试人格_{unique_suffix}",
        )
        character_obj = character.create(db, obj_in=character_data)
        self.data_manager.track_character(character_obj)

        # 搜索角色 - 使用角色名称中的关键词
        search_request = {
            "query": "搜索测试角色",  # 使用角色名称中的关键词
            "search_type": "text",
            "limit": 10,
            "offset": 0,
        }

        from app.models.character import CharacterSearchRequest

        search_req = CharacterSearchRequest(**search_request)
        result = character.search(db, search_request=search_req)

        # 检查结果中是否包含我们创建的角色
        found_character = None
        for search_result in result.results:
            if search_result.character.id == character_obj.id:
                found_character = search_result
                break
        
        assert found_character is not None
        assert found_character.character.name == unique_name


class TestCharacterTagCRUD:
    """角色标签CRUD测试类"""

    @pytest.fixture(autouse=True)
    def setup_test_data_manager(self, db: Session):
        """为每个测试方法设置数据管理器"""
        self.data_manager = TestDataManager(db)
        yield
        # 测试结束后清理数据
        self.data_manager.cleanup()

    def test_create_character_tag(self, db: Session) -> None:
        """测试创建标签"""
        tag_data = CharacterTagCreate(
            name="测试标签",
            description="这是一个测试标签",
            color="#FF0000",
        )

        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        assert tag_obj.name == tag_data.name
        assert tag_obj.description == tag_data.description
        assert tag_obj.color == tag_data.color
        assert tag_obj.id is not None

    def test_get_character_tag(self, db: Session) -> None:
        """测试获取标签"""
        # 创建测试标签
        tag_data = CharacterTagCreate(
            name="获取测试标签",
            description="用于测试获取",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 获取标签
        retrieved_tag = character_tag.get(db, id=tag_obj.id)

        assert retrieved_tag is not None
        assert retrieved_tag.id == tag_obj.id
        assert retrieved_tag.name == tag_obj.name

    def test_get_character_tag_by_name(self, db: Session) -> None:
        """测试根据名称获取标签"""
        # 使用唯一的名称避免冲突
        unique_name = f"名称测试标签_{uuid.uuid4().hex[:8]}"
        tag_data = CharacterTagCreate(
            name=unique_name,
            description="用于测试名称获取",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        retrieved_tag = character_tag.get_by_name(db, name=tag_obj.name)

        assert retrieved_tag is not None
        assert retrieved_tag.id == tag_obj.id
        assert retrieved_tag.name == tag_obj.name

    def test_get_multi_character_tags(self, db: Session) -> None:
        """测试获取多个标签"""
        # 先获取当前总数
        _, initial_total = character_tag.get_multi(db, skip=0, limit=1000)

        # 创建多个测试标签，使用唯一名称
        unique_suffix = uuid.uuid4().hex[:8]
        for i in range(3):
            tag_data = CharacterTagCreate(
                name=f"多标签测试_{unique_suffix}_{i}",
                description=f"多标签测试描述_{unique_suffix}_{i}",
            )
            tag_obj = character_tag.create(db, obj_in=tag_data)
            self.data_manager.track_tag(tag_obj)

        tags, total = character_tag.get_multi(db, skip=0, limit=10)

        assert len(tags) >= 3
        assert total == initial_total + 3

    def test_update_character_tag(self, db: Session) -> None:
        """测试更新标签"""
        # 创建测试标签，使用唯一名称
        unique_name = f"更新测试标签_{uuid.uuid4().hex[:8]}"
        tag_data = CharacterTagCreate(
            name=unique_name,
            description="原始描述",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 更新标签
        update_data = CharacterTagUpdate(
            description="更新后的描述",
            color="#00FF00",
        )
        updated_tag = character_tag.update(db, db_obj=tag_obj, obj_in=update_data)

        assert updated_tag.description == update_data.description
        assert updated_tag.color == update_data.color
        assert updated_tag.name == tag_obj.name  # 未更新的字段保持不变

    def test_delete_character_tag(self, db: Session) -> None:
        """测试删除标签"""
        # 创建测试标签，使用唯一名称
        unique_name = f"删除测试标签_{uuid.uuid4().hex[:8]}"
        tag_data = CharacterTagCreate(
            name=unique_name,
            description="用于测试删除",
        )
        tag_obj = character_tag.create(db, obj_in=tag_data)
        self.data_manager.track_tag(tag_obj)

        # 删除标签
        deleted_tag = character_tag.delete(db, id=tag_obj.id)

        assert deleted_tag is not None

        # 验证标签已被删除
        retrieved_tag = character_tag.get(db, id=tag_obj.id)
        assert retrieved_tag is None
