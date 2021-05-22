from typing import TYPE_CHECKING, List
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .course_set import CourseSetMembership  # noqa: F401
    from .university import University  # noqa: F401
    from .track import Track  # noqa: F401
    from .term import Term  # noqa: F401
    from .faculty import Faculty  # noqa: F401
    from .department import Department  # noqa: F401


course_faculty = Table(
    "course_faculty",
    Base.metadata,
    Column("university_id", Integer, primary_key=True),
    Column("course_id", Text, primary_key=True),
    Column("faculty_id", Text, primary_key=True),
    ForeignKeyConstraint(
        ["university_id", "course_id"], ["course.university_id", "course.id"]
    ),
    ForeignKeyConstraint(
        ["university_id", "faculty_id"], ["faculty.university_id", "faculty.id"]
    ),
)

course_department = Table(
    "course_department",
    Base.metadata,
    Column("university_id", Integer, primary_key=True),
    Column("course_id", Text, primary_key=True),
    Column("department_id", Text, primary_key=True),
    ForeignKeyConstraint(
        ["university_id", "course_id"], ["course.university_id", "course.id"]
    ),
    ForeignKeyConstraint(
        ["university_id", "department_id"],
        ["department.university_id", "department.id"],
    ),
)

course_track = Table(
    "course_track",
    Base.metadata,
    Column("university_id", Integer, primary_key=True),
    Column("course_id", Text, primary_key=True),
    Column("track_id", Text, primary_key=True),
    ForeignKeyConstraint(
        ["university_id", "course_id"], ["course.university_id", "course.id"]
    ),
    ForeignKeyConstraint(
        ["university_id", "track_id"], ["track.university_id", "track.id"]
    ),
)


class Course(Base):
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

    term: Mapped["Term"] = relationship("Term", lazy="joined")

    faculties: Mapped["Faculty"] = relationship(
        "Faculty", secondary=course_faculty, back_populates="courses"
    )
    tracks: Mapped["Track"] = relationship(
        "Track", secondary=course_track, back_populates="courses"
    )
    departments: Mapped["Department"] = relationship(
        "Department", secondary=course_department, back_populates="courses"
    )

    memberships: Mapped[List["CourseSetMembership"]] = relationship(
        "CourseSetMembership", back_populates="course"
    )
