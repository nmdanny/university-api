from __future__ import annotations
from sqlalchemy import (
    Table,
    Column,
    Integer,
    Text,
    Enum,
    ForeignKeyConstraint,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
)
import enum
from sqlalchemy.orm import Mapped, relationship, foreign, remote
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, ExtraData
from typing import Optional, List

from .university import University
from .course import Course
from .course_set import CourseSet, CourseSetMembership
from .track import Track

dag_edge_assoc = Table(
    "dag_edge",
    Base.metadata,
    Column("from_node_id", Integer, ForeignKey("dagnode.node_id"), primary_key=True),
    Column("to_node_id", Integer, ForeignKey("dagnode.node_id"), primary_key=True),
    CheckConstraint("from_node_id != to_node_id", name="no_self_loops"),
)


class DAGNode(Base):
    node_id: Mapped[int] = Column(Integer, primary_key=True, autoincrement=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), nullable=False
    )
    node_type: Mapped[str] = Column(Text, nullable=False)
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped[University] = relationship(University)
    parents: Mapped[List[DAGNode]] = relationship(
        "DAGNode",
        secondary=dag_edge_assoc,
        primaryjoin=(node_id == dag_edge_assoc.c.to_node_id),
        secondaryjoin=(node_id == dag_edge_assoc.c.from_node_id),
        backref="children",
    )

    children: Mapped[List[DAGNode]]
    __mapper_args__ = {"polymorphic_identity": "DAGNode", "polymorphic_on": node_type}


class DAGRootNode(DAGNode):
    node_id: Mapped[int] = Column(
        Integer, ForeignKey("dagnode.node_id"), primary_key=True
    )
    university_id: Mapped[int] = Column(Integer)
    track_id: Mapped[str] = Column(Text, nullable=False)

    track: Mapped[Track] = relationship(Track, backref="dag_root")

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "track_id"], ["track.university_id", "track.id"],
        ),
    )
    __mapper_args__ = {"polymorphic_identity": "DAGRootNode"}


class CourseSetNode(DAGNode):
    node_id: Mapped[int] = Column(
        Integer, ForeignKey("dagnode.node_id"), primary_key=True
    )
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), nullable=False
    )
    course_set_id: Mapped[int] = Column(Integer, nullable=False)
    course_set: Mapped[CourseSet] = relationship(CourseSet, backref="nodes")

    __table_args__ = (
        ForeignKeyConstraint(
            ["university_id", "course_set_id"],
            ["courseset.university_id", "courseset.id"],
        ),
    )
    __mapper_args__ = {
        "polymorphic_identity": "CourseSetNode",
    }


def singleton_course_node(course: Course) -> CourseSetNode:
    """ Creates a new, singleton course set and node object """
    course_set = CourseSet(
        university=course.university, min_subset_size=1, max_subset_size=1,
    )
    course_set.courses.append(course)
    node = CourseSetNode(university=course.university, course_set=course_set)
    return node


class ORNode(DAGNode):
    node_id: Mapped[int] = Column(
        Integer, ForeignKey("dagnode.node_id"), primary_key=True
    )

    __mapper_args__ = {
        "polymorphic_identity": "ORNode",
    }
