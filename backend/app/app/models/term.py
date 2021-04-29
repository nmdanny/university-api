from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.postgresql import JSON

from app.db.base_class import Base, Translations


class Term(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name_translations: Translations = Column(JSON, default=lambda: {})
