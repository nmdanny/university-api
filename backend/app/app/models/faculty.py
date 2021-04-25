from typing import TYPE_CHECKING, List

from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .department import Department  # noqa: F401


class Faculty(Base):
    """ A faculty/school is a division within a university/college, and may have
        one or more departments. """

    id: Mapped[str] = Column(Text, primary_key=True)
    university_id: Mapped[int] = Column(
        Integer, ForeignKey("university.id"), primary_key=True
    )
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    university: Mapped["University"] = relationship(
        "University", back_populates="faculties"
    )

    departments: Mapped[List["Department"]] = relationship(
        "Department", back_populates="faculty"
    )
