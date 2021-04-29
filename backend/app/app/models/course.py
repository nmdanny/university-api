from typing import TYPE_CHECKING, List
from sqlalchemy import (
    Table,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    CheckConstraint,
    Integer,
    Text,
)
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.dialects.postgresql import JSON
from app.db.base_class import Base, Translations, ExtraData

if TYPE_CHECKING:
    from .university import University  # noqa: F401
    from .track import Track  # noqa: F401
    from .term import Term  # noqa: F401


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
