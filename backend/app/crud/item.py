import uuid

from app.models.item import Item, ItemCreate
from sqlmodel import Session


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    """创建新项目"""
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item
