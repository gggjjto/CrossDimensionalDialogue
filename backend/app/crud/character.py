import uuid
from typing import List, Optional, Tuple

from sqlmodel import Session, select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.models.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
    CharacterPublic,
    CharacterTag,
    CharacterTagCreate,
    CharacterTagUpdate,
    CharacterTagMap,
    CharacterSearchRequest,
    CharacterSearchResult,
    CharacterSearchResponse,
)


class CharacterCRUD:
    """角色CRUD操作类"""

    def create(self, db: Session, *, obj_in: CharacterCreate) -> Character:
        """创建角色"""
        # 创建角色基本信息
        character_data = obj_in.model_dump(exclude={"tag_ids"})
        character = Character(**character_data)
        db.add(character)
        db.flush()  # 获取角色ID

        # 处理标签关联
        if obj_in.tag_ids:
            self._create_character_tag_relations(db, character.id, obj_in.tag_ids)

        db.commit()
        db.refresh(character)
        return character

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[Character]:
        """根据ID获取角色"""
        statement = (
            select(Character)
            .where(Character.id == id)
            .options(selectinload(Character.tag_relations).selectinload(CharacterTagMap.tag))
        )
        return db.exec(statement).first()

    def get_by_name(self, db: Session, *, name: str) -> Optional[Character]:
        """根据名称获取角色"""
        statement = (
            select(Character)
            .where(Character.name == name)
            .options(selectinload(Character.tag_relations).selectinload(CharacterTagMap.tag))
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
        tag_ids: Optional[List[uuid.UUID]] = None,
    ) -> Tuple[List[Character], int]:
        """获取角色列表"""
        statement = (
            select(Character)
            .options(selectinload(Character.tag_relations).selectinload(CharacterTagMap.tag))
        )

        # 应用过滤条件
        conditions = []
        if is_active is not None:
            conditions.append(Character.is_active == is_active)
        if tag_ids:
            conditions.append(
                Character.id.in_(
                    select(CharacterTagMap.character_id).where(
                        CharacterTagMap.tag_id.in_(tag_ids)
                    )
                )
            )

        if conditions:
            statement = statement.where(and_(*conditions))

        # 获取总数
        count_statement = select(func.count(Character.id))
        if conditions:
            count_statement = count_statement.where(and_(*conditions))
        total = db.exec(count_statement).one()

        # 获取数据
        statement = statement.offset(skip).limit(limit).order_by(Character.created_at.desc())
        characters = db.exec(statement).all()

        return characters, total

    def update(self, db: Session, *, db_obj: Character, obj_in: CharacterUpdate) -> Character:
        """更新角色"""
        update_data = obj_in.model_dump(exclude_unset=True, exclude={"tag_ids"})
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        # 处理标签关联更新
        if obj_in.tag_ids is not None:
            # 删除现有关联
            db.exec(
                select(CharacterTagMap).where(CharacterTagMap.character_id == db_obj.id)
            ).delete()
            # 创建新关联
            self._create_character_tag_relations(db, db_obj.id, obj_in.tag_ids)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> Optional[Character]:
        """删除角色（软删除）"""
        character = self.get(db, id=id)
        if character:
            character.is_active = False
            db.add(character)
            db.commit()
            db.refresh(character)
        return character

    def hard_delete(self, db: Session, *, id: uuid.UUID) -> Optional[Character]:
        """硬删除角色"""
        character = self.get(db, id=id)
        if character:
            db.delete(character)
            db.commit()
        return character

    def search(
        self, db: Session, *, search_request: CharacterSearchRequest
    ) -> CharacterSearchResponse:
        """搜索角色"""
        if search_request.search_type == "text":
            return self._text_search(db, search_request)
        elif search_request.search_type == "vector":
            return self._vector_search(db, search_request)
        elif search_request.search_type == "hybrid":
            return self._hybrid_search(db, search_request)
        else:
            raise ValueError(f"不支持的搜索类型: {search_request.search_type}")

    def _text_search(
        self, db: Session, search_request: CharacterSearchRequest
    ) -> CharacterSearchResponse:
        """文本搜索"""
        query = search_request.query.lower()
        
        # 构建搜索条件
        conditions = [
            or_(
                Character.name.ilike(f"%{query}%"),
                Character.short_bio.ilike(f"%{query}%"),
                Character.persona_text.ilike(f"%{query}%"),
            )
        ]

        if search_request.is_active is not None:
            conditions.append(Character.is_active == search_request.is_active)

        if search_request.tag_ids:
            conditions.append(
                Character.id.in_(
                    select(CharacterTagMap.character_id).where(
                        CharacterTagMap.tag_id.in_(search_request.tag_ids)
                    )
                )
            )

        # 获取总数
        count_statement = select(func.count(Character.id)).where(and_(*conditions))
        total = db.exec(count_statement).one()

        # 获取数据
        statement = (
            select(Character)
            .where(and_(*conditions))
            .options(selectinload(Character.tag_relations).selectinload(CharacterTagMap.tag))
            .offset(search_request.offset)
            .limit(search_request.limit)
            .order_by(Character.created_at.desc())
        )
        characters = db.exec(statement).all()

        # 构建结果
        results = [
            CharacterSearchResult(
                character=CharacterPublic.model_validate(character),
                match_type="text",
            )
            for character in characters
        ]

        return CharacterSearchResponse(
            results=results,
            total=total,
            query=search_request.query,
            search_type=search_request.search_type,
        )

    def _vector_search(
        self, db: Session, search_request: CharacterSearchRequest
    ) -> CharacterSearchResponse:
        """向量搜索（暂时返回空结果，后续集成pgvector）"""
        # TODO: 实现pgvector搜索
        return CharacterSearchResponse(
            results=[],
            total=0,
            query=search_request.query,
            search_type=search_request.search_type,
        )

    def _hybrid_search(
        self, db: Session, search_request: CharacterSearchRequest
    ) -> CharacterSearchResponse:
        """混合搜索（文本+向量）"""
        # 暂时只使用文本搜索
        return self._text_search(db, search_request)

    def _create_character_tag_relations(
        self, db: Session, character_id: uuid.UUID, tag_ids: List[uuid.UUID]
    ) -> None:
        """创建角色-标签关联关系"""
        for tag_id in tag_ids:
            relation = CharacterTagMap(character_id=character_id, tag_id=tag_id)
            db.add(relation)


class CharacterTagCRUD:
    """角色标签CRUD操作类"""

    def create(self, db: Session, *, obj_in: CharacterTagCreate) -> CharacterTag:
        """创建标签"""
        tag = CharacterTag(**obj_in.model_dump())
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

    def get(self, db: Session, *, id: uuid.UUID) -> Optional[CharacterTag]:
        """根据ID获取标签"""
        return db.get(CharacterTag, id)

    def get_by_name(self, db: Session, *, name: str) -> Optional[CharacterTag]:
        """根据名称获取标签"""
        statement = select(CharacterTag).where(CharacterTag.name == name)
        return db.exec(statement).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> Tuple[List[CharacterTag], int]:
        """获取标签列表"""
        # 获取总数
        count_statement = select(func.count(CharacterTag.id))
        total = db.exec(count_statement).one()

        # 获取数据
        statement = (
            select(CharacterTag)
            .offset(skip)
            .limit(limit)
            .order_by(CharacterTag.name)
        )
        tags = db.exec(statement).all()

        return tags, total

    def update(
        self, db: Session, *, db_obj: CharacterTag, obj_in: CharacterTagUpdate
    ) -> CharacterTag:
        """更新标签"""
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: uuid.UUID) -> Optional[CharacterTag]:
        """删除标签"""
        tag = self.get(db, id=id)
        if tag:
            db.delete(tag)
            db.commit()
        return tag


# 创建CRUD实例
character = CharacterCRUD()
character_tag = CharacterTagCRUD()
