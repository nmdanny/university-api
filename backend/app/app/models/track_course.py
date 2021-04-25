from sqlalchemy import Table, Column, Text, Integer, ForeignKeyConstraint
from app.db.base_class import Base


track_course = Table(
    "track_course_association",
    Base.metadata,
    Column("track_id", Text, primary_key=True),
    Column("course_id", Text, primary_key=True),
    Column("university_id", Integer, primary_key=True),
    ForeignKeyConstraint(
        ["track_id", "university_id"],
        ["track.id", "track.university_id"],
    ),
    ForeignKeyConstraint(
        ["course_id", "university_id"], ["course.id", "course.university_id"]
    ),
)
