from sqlalchemy import Table, Column, Integer, Text, ForeignKeyConstraint
from app.db.base_class import Base


track_department = Table(
    "track_department_association",
    Base.metadata,
    Column("university_id", Integer, primary_key=True),
    Column("track_id", Text, primary_key=True),
    Column("faculty_id", Text, primary_key=True),
    Column("department_id", Text, primary_key=True),
    ForeignKeyConstraint(
        ["university_id", "track_id"], ["track.university_id", "track.id"],
    ),
    ForeignKeyConstraint(
        ["university_id", "faculty_id", "department_id"],
        ["department.university_id", "department.faculty_id", "department.id"],
    ),
)
