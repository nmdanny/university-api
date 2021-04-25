from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

from .track_course import track_course

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .track import Track  # noqa: F401
    from .term import Term  # noqa: F401


class Course(Base):
    id: Mapped[str] = Column(String(30), primary_key=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    term_id: Mapped[int] = Column(Integer, ForeignKey("term.id"))
    university: Mapped["University"] = relationship(
        "University", back_populates="courses"
    )

    tracks: Mapped[List["Track"]] = relationship(
        "Track", secondary=track_course, back_populates="courses"
    )

    term: Mapped["Term"] = relationship("Term")

    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})
