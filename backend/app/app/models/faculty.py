from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .track import Track  # noqa: F401


class Faculty(Base):
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped["University"] = relationship(
        "University", back_populates="faculties"
    )

    tracks: Mapped[List["Track"]] = relationship("Track", back_populates="faculty")

    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})
