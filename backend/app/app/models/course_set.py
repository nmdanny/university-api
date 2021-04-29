from sqlalchemy import (
    Column,
    Integer,
    Text,
    Enum,
    ForeignKeyConstraint,
    ForeignKey,
    CheckConstraint,
)
import enum
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, ExtraData
from typing import TYPE_CHECKING, Optional, List

from .course import Course  # noqa: F401
from .university import University
if TYPE_CHECKING:
    from .track import Track  # noqa: F401
    from .course import Course  # noqa: F401

DEFAULT_MAX_INT = 9999


class CourseSet(Base):
    """ Represents a set of courses which must be taken in order to fulfill academic
        requirements, either as part of a track or globally.

        It is possible to place various restrictions on this set, such as,
        the minimal/maximal number of credits, or the minimal/maximal size of a subset
        of courses which should be chosen from this set.

        A course set is also a node within a DAG, which allows expressing
        more complicated tracks, such as prerequisites, choice between paths,
        etc.
    """

    # id within the tree
    id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)

    # defines the track to which this tree node belongs (or just the university)
    university_id: Mapped[int] = Column(Integer, ForeignKey("university.id"), primary_key=True)
    track_id: Mapped[Optional[str]] = Column(Text, nullable=True)

    # requirements and metadata of this set
    min_subset_size: Mapped[int] = Column(Integer)
    max_subset_size: Mapped[int] = Column(Integer, default=DEFAULT_MAX_INT)
    min_credits: Mapped[int] = Column(Integer, default=0)
    max_credits: Mapped[int] = Column(Integer, default=DEFAULT_MAX_INT)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped[University] = relationship(University)

    track: Mapped[Optional["Track"]] = relationship(
        "Track", back_populates="root_course_set"
    )

    # leafs (individual courses that are members of this set)
    course_memberships: Mapped[List["CourseSetMembership"]] = relationship(
        "CourseSetMembership", back_populates="set",
    )
    courses: Mapped[List["Course"]] = association_proxy("course_memberships", "course")

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "track_id"], ["track.university_id", "track.id"]
        ),
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

    set: Mapped["CourseSet"] = relationship(
        "CourseSet", back_populates="course_memberships",
    )
    course: Mapped["Course"] = relationship("Course")

    def __init__(self, course: Course):
        self.course = course

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "set_id"], ["courseset.university_id", "courseset.id"],
        ),
        ForeignKeyConstraint(
            ["university_id", "course_id"], ["course.university_id", "course.id"]
        ),
    )


class CourseSetEdgeType(enum.Enum):
    AndThen = 0
    And = 1
    Or = 2


class CourseSetEdge(Base):
    university_id: Mapped[int] = Column(Integer, primary_key=True)
    from_set_id: Mapped[int] = Column(Integer, primary_key=True)
    to_set_id: Mapped[int] = Column(Integer, primary_key=True)
    edge_type: Mapped[CourseSetEdgeType] = Column(
        Enum(CourseSetEdgeType), default=CourseSetEdgeType.And
    )
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    from_set: Mapped[CourseSet] = relationship(
        CourseSet,
        primaryjoin=(
            (university_id == CourseSet.university_id) & (from_set_id == CourseSet.id)
        ),
        backref="outgoing_edges",
        overlaps="to_set, coursesetedge",
    )

    to_set: Mapped[CourseSet] = relationship(
        CourseSet,
        primaryjoin=(
            (university_id == CourseSet.university_id) & (to_set_id == CourseSet.id)
        ),
        backref="incoming_edges",
        overlaps="from_set, coursesetedge",
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "from_set_id"],
            ["courseset.university_id", "courseset.id"],
        ),
        ForeignKeyConstraint(
            ["university_id", "to_set_id"], ["courseset.university_id", "courseset.id"],
        ),
        CheckConstraint(from_set_id != to_set_id),
    )
