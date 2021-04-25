from typing import TYPE_CHECKING, List
import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKeyConstraint
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, ExtraData, Translations

from .track_course import track_course

if TYPE_CHECKING:
    from .faculty import Faculty  # noqa: F401
    from .course import Course  # noqa: F401


class DegreeType(enum.Enum):
    """ Type of degree for a track
        Numbered according to ISCED
        https://en.wikipedia.org/wiki/International_Standard_Classification_of_Education
    """

    Bachelors = 6
    Masters = 7
    Doctoral = 8


class Track(Base):
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    faculty_id: Mapped[int] = Column(Integer, primary_key=True)
    university_id: Mapped[int] = Column(Integer, primary_key=True)
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    degree: Mapped[DegreeType] = Column(Enum(DegreeType), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["faculty_id", "university_id"], ["faculty.id", "faculty.university_id"]
        ),
    )

    faculty: Mapped["Faculty"] = relationship("Faculty", back_populates="tracks")

    courses: Mapped[List["Course"]] = relationship(
        "Course", secondary=track_course, back_populates="tracks"
    )

    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})
