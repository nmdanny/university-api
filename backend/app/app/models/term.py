from typing import TYPE_CHECKING  # noqa: F401

from sqlalchemy import Column, Integer, String  # noqa: F401
from sqlalchemy.orm import relationship, Mapped  # noqa: F401
from sqlalchemy.dialects.postgresql import JSON

from app.db.base_class import Base, Translations


class Term(Base):
    id: Mapped[int] = Column(Integer, primary_key=True)
    name_translations: Translations = Column(JSON, default=lambda: {})
