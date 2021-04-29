from typing import TYPE_CHECKING, List
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    CheckConstraint,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship, Mapped, foreign
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .track import Track  # noqa: F401
    from .term import Term  # noqa: F401


class Course(Base):
    """ A course belongs to a university, and can be associated to
        various tracks(and indirectly, to various departments/faculties) 
    """

    # Uniquely identifies the course within the entire university
    id: Mapped[str] = Column(Text, primary_key=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    term_id: Mapped[int] = Column(Integer, ForeignKey("term.id"))
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})
    course_credits: Mapped[int] = Column(Integer)

    university: Mapped["University"] = relationship(
        "University", back_populates="courses"
    )

    term: Mapped["Term"] = relationship("Term")

    prerequisites: Mapped[List["CoursePrerequisite"]]
    prereqsuite_for: Mapped[List["CoursePrerequisite"]]


class CoursePrerequisite(Base):
    """ Specifies a course prerequisite """

    university_id: Mapped[int] = Column(Integer, primary_key=True)
    course_id: Mapped[str] = Column(Text, primary_key=True)
    prerequisite_id: Mapped[str] = Column(Text, primary_key=True)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    prerequisite: Mapped[Course] = relationship(
        Course,
        foreign_keys=[university_id, prerequisite_id],
        backref="prerequisite_for"
    )

    course: Mapped[Course] = relationship(
        Course,
        foreign_keys=[university_id, course_id],
        backref="prerequisites"
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "course_id"], ["course.university_id", "course.id"]
        ),
        ForeignKeyConstraint(
            ["university_id", "prerequisite_id"], ["course.university_id", "course.id"]
        ),
        CheckConstraint(course_id != prerequisite_id),
    )
