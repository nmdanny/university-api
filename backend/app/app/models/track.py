from typing import TYPE_CHECKING, List
import enum

from sqlalchemy import Column, Integer, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, ExtraData, Translations
from .course import course_track


if TYPE_CHECKING:
    from .course_dag import DAGRootNode  # noqa: F401
    from .university import University  # noqa: F401
    from .department import Department  # noqa: F401
    from .course import Course  # noqa: F401


class DegreeType(str, enum.Enum):
    """ Type of degree for a track """

    Misc = 'Misc'
    Bachelors = 'Bachelors'
    Masters = 'Masters'
    Doctoral = 'Doctoral'


class Track(Base):
    """ A track within a university is usually a path to getting a degree
        Most tracks belong to a particular department & faculty,
        but some tracks can cross departments or even faculties.
    """

    # Uniquely identifies the track within a university
    id: Mapped[str] = Column(Text, primary_key=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    degree: Mapped[DegreeType] = Column(Enum(DegreeType), nullable=False)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped["University"] = relationship(
        "University", back_populates="tracks"
    )

    courses: Mapped[List["Course"]] = relationship(
        "Course", secondary=course_track, back_populates="tracks"
    )
