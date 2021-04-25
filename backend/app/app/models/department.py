from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKeyConstraint, Integer, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData
from .track_department import track_department

if TYPE_CHECKING:
    from .faculty import Faculty  # noqa: F401
    from .track import Track  # noqa: F401


class Department(Base):
    """ A department belongs to a faculty, and offers one or more tracks """

    id: Mapped[str] = Column(Text, primary_key=True)
    university_id: Mapped[int] = Column(Integer, primary_key=True)
    faculty_id: Mapped[str] = Column(Text, primary_key=True)
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    tracks: Mapped[List["Track"]] = relationship(
        "Track", secondary=track_department, back_populates="departments"
    )
    faculty: Mapped["Faculty"] = relationship("Faculty", back_populates="departments")

    __table_args__ = (
        ForeignKeyConstraint(
            ["faculty_id", "university_id"], ["faculty.id", "faculty.university_id"]
        ),
    )
