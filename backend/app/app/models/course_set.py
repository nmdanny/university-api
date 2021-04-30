from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    ForeignKeyConstraint,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, relationship, foreign, remote
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, ExtraData
from typing import Optional, List

from .course import Course
from .track import Track
from .university import University


class CourseSet(Base):
    """ Represents a set of courses which must be taken in order to fulfill academic
        requirements, either as part of a track or globally.

        It is possible to place various restrictions on this set, such as,
        the minimal/maximal number of credits, or the minimal/maximal size of a subset
        of courses which should be chosen from this set.

        A course set is also a node within a DAG, which allows expressing
        more complicated tracks, such as prerequisites and choice between paths.
    """

    # id within the tree
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )

    # requirements and metadata of this set
    min_subset_size: Mapped[Optional[int]] = Column(Integer, nullable=True)
    max_subset_size: Mapped[Optional[int]] = Column(Integer, nullable=True)
    min_credits: Mapped[Optional[int]] = Column(Integer, nullable=True)
    max_credits: Mapped[Optional[int]] = Column(Integer, nullable=True)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped[University] = relationship(University)

    # leafs (individual courses that are members of this set)
    course_memberships: Mapped[List["CourseSetMembership"]] = relationship(
        "CourseSetMembership", back_populates="set",
    )
    courses: Mapped[List[Course]] = association_proxy("course_memberships", "course")

    __table_args__ = (
        CheckConstraint(
            (min_subset_size <= max_subset_size) & (min_credits <= max_credits)
        ),
    )


class CourseSetMembership(Base):
    """ Indicates membership of a course in a course set. """

    university_id: Mapped[int] = Column(Integer, primary_key=True)
    set_id: Mapped[int] = Column(Integer, primary_key=True)
    course_id: Mapped[str] = Column(Text, primary_key=True)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    set: Mapped[CourseSet] = relationship(
        CourseSet,
        back_populates="course_memberships"
    )
    course: Mapped[Course] = relationship(
        Course, back_populates="memberships"
    )

    def __init__(self, course: Course):
        self.course = course

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "set_id"], ["courseset.university_id", "courseset.id"]
        ),
        ForeignKeyConstraint(
            ["university_id", "course_id"], ["course.university_id", "course.id"]
        ),
    )
