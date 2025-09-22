"""
测试数据管理器
用于管理测试中创建的数据，确保测试结束后清理自己插入的数据
"""
import uuid
from typing import List, Set
from sqlmodel import Session, delete

from app.models.character import Character, CharacterTag, CharacterTagMap, CharacterEmbedding


class TestDataManager:
    """测试数据管理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.created_character_ids: Set[uuid.UUID] = set()
        self.created_tag_ids: Set[uuid.UUID] = set()
        self.created_character_tag_map_ids: Set[uuid.UUID] = set()
        self.created_embedding_ids: Set[uuid.UUID] = set()
    
    def track_character(self, character: Character) -> Character:
        """跟踪创建的角色"""
        self.created_character_ids.add(character.id)
        return character
    
    def track_tag(self, tag: CharacterTag) -> CharacterTag:
        """跟踪创建的标签"""
        self.created_tag_ids.add(tag.id)
        return tag
    
    def track_character_tag_map(self, character_tag_map: CharacterTagMap) -> CharacterTagMap:
        """跟踪创建的角色标签关系"""
        self.created_character_tag_map_ids.add(character_tag_map.id)
        return character_tag_map
    
    def track_embedding(self, embedding: CharacterEmbedding) -> CharacterEmbedding:
        """跟踪创建的向量"""
        self.created_embedding_ids.add(embedding.id)
        return embedding
    
    def cleanup(self):
        """清理跟踪的数据"""
        # 按依赖关系顺序删除
        if self.created_embedding_ids:
            statement = delete(CharacterEmbedding).where(
                CharacterEmbedding.id.in_(self.created_embedding_ids)
            )
            self.db.execute(statement)
        
        if self.created_character_tag_map_ids:
            statement = delete(CharacterTagMap).where(
                CharacterTagMap.id.in_(self.created_character_tag_map_ids)
            )
            self.db.execute(statement)
        
        if self.created_character_ids:
            statement = delete(Character).where(
                Character.id.in_(self.created_character_ids)
            )
            self.db.execute(statement)
        
        if self.created_tag_ids:
            statement = delete(CharacterTag).where(
                CharacterTag.id.in_(self.created_tag_ids)
            )
            self.db.execute(statement)
        
        self.db.commit()
        
        # 清空跟踪集合
        self.created_character_ids.clear()
        self.created_tag_ids.clear()
        self.created_character_tag_map_ids.clear()
        self.created_embedding_ids.clear()


def create_test_character(
    db: Session, 
    data_manager: TestDataManager,
    name: str = "测试角色",
    short_bio: str = "测试角色简介",
    persona_text: str = "测试角色人格",
    **kwargs
) -> Character:
    """创建测试角色并跟踪"""
    from app.crud.character import character
    from app.models.character import CharacterCreate
    
    character_data = CharacterCreate(
        name=name,
        short_bio=short_bio,
        persona_text=persona_text,
        **kwargs
    )
    
    character_obj = character.create(db, obj_in=character_data)
    return data_manager.track_character(character_obj)


def create_test_tag(
    db: Session,
    data_manager: TestDataManager,
    name: str = "测试标签",
    description: str = "测试标签描述",
    **kwargs
) -> CharacterTag:
    """创建测试标签并跟踪"""
    from app.crud.character import character_tag
    from app.models.character import CharacterTagCreate
    
    tag_data = CharacterTagCreate(
        name=name,
        description=description,
        **kwargs
    )
    
    tag_obj = character_tag.create(db, obj_in=tag_data)
    return data_manager.track_tag(tag_obj)
