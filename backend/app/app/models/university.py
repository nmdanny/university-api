from typing import TYPE_CHECKING, List

from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .course import Course  # noqa: F401
    from .faculty import Faculty  # noqa: F401
    from .track import Track  # noqa: F401


class University(Base):
    """ A university/college is a collection of faculties and courses """

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name_translations: Translations = Column(JSON, nullable=False, default=lambda: {})
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})

    courses: Mapped[List["Course"]] = relationship(
        "Course", back_populates="university"
    )

    faculties: Mapped[List["Faculty"]] = relationship(
        "Faculty", back_populates="university"
    )

    tracks: Mapped[List["Track"]] = relationship("Track", back_populates="university")
