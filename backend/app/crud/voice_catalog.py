from __future__ import annotations

from typing import Dict, List, Optional, Tuple, Union

from sqlmodel import Session, select, func

from app.models.voice_catalog import (
    VoiceCatalog,
    VoiceCatalogCreate,
    VoiceCatalogUpdate,
)


class VoiceCatalogCRUD:
    """音色目录 CRUD。"""

    def create(self, db: Session, *, obj_in: VoiceCatalogCreate) -> VoiceCatalog:
        db_obj = VoiceCatalog.model_validate(obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, *, id) -> Optional[VoiceCatalog]:
        return db.get(VoiceCatalog, id)

    def get_by_voice(
        self, db: Session, *, provider: str, voice: str
    ) -> Optional[VoiceCatalog]:
        statement = select(VoiceCatalog).where(
            VoiceCatalog.provider == provider, VoiceCatalog.voice == voice
        )
        return db.exec(statement).first()

    def get_multi(
        self,
        db: Session,
        *,
        provider: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Union[str, bool]]] = None,
    ) -> Tuple[List[VoiceCatalog], int]:
        statement = select(VoiceCatalog)
        if provider:
            statement = statement.where(VoiceCatalog.provider == provider)
        if filters:
            for key, value in filters.items():
                if hasattr(VoiceCatalog, key) and value is not None:
                    statement = statement.where(getattr(VoiceCatalog, key) == value)

        count_statement = select(func.count()).select_from(statement.subquery())
        total = db.exec(count_statement).one()

        statement = (
            statement.offset(skip).limit(limit).order_by(VoiceCatalog.created_at.desc())
        )
        items = db.exec(statement).all()
        return items, total

    def update(
        self, db: Session, *, db_obj: VoiceCatalog, obj_in: VoiceCatalogUpdate
    ) -> VoiceCatalog:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id) -> Optional[VoiceCatalog]:
        obj = db.get(VoiceCatalog, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


voice_catalog_crud = VoiceCatalogCRUD()
