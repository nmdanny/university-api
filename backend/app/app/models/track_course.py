from sqlalchemy import Table, Column, Integer, String, ForeignKeyConstraint
from app.db.base_class import Base


track_course = Table(
    "track_course_association",
    Base.metadata,
    Column("track_id", Integer, primary_key=True),
    Column("track_faculty_id", Integer, primary_key=True),
    Column("course_id", String, primary_key=True),
    Column("university_id", Integer, primary_key=True),
    ForeignKeyConstraint(
        ["track_id", "track_faculty_id", "university_id"],
        ["track.id", "track.faculty_id", "track.university_id"],
    ),
    ForeignKeyConstraint(
        ["course_id", "university_id"], ["course.id", "course.university_id"]
    ),
)
