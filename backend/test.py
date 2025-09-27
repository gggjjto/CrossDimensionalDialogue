from app.core.db import engine
from sqlmodel import SQLModel


SQLModel.metadata.drop_all(engine)
