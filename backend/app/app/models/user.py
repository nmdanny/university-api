from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, Mapped

from app.db.base_class import Base

if TYPE_CHECKING:
    from .item import Item  # noqa: F401


class User(Base):
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = Column(String, nullable=False)
    is_active: Mapped[bool] = Column(Boolean(), default=True)
    is_superuser: Mapped[bool] = Column(Boolean(), default=False)
    items: Mapped[List["Item"]] = relationship("Item", back_populates="owner")
