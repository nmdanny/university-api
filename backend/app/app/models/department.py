from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData
from .course import course_department

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .course import Course  # noqa: F401


class Department(Base):
    """ A department belongs to a faculty, and offers one or more tracks """

    id: Mapped[str] = Column(Text, primary_key=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped["University"] = relationship(
        "University", back_populates="departments"
    )

    courses: Mapped[List["Course"]] = relationship(
        "Course", secondary=course_department, back_populates="departments"
    )
