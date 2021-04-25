from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.dialects.postgresql import JSON

from app.db.base_class import Base, Translations, ExtraData


class Term(Base):
    """ A term is a period of an academic year in which a course is held.
        Some universities may use semesters(2 terms in a year), some might use
        trimesters and so on. There might also be special kinds of terms, like a
        whole-year course, or a special summer course and so on.

        A term in the database does not have a clear scheduling. For example, if we have
        terms for 'Semester 1' and 'Semester 2', it's likely they will represent
        different dates between universities of different countries, or
        even within the same country.
    """

    id: Mapped[int] = Column(Integer, primary_key=True)
    name_translations: Translations = Column(JSON, default=lambda: {})
    extra_data: ExtraData = Column(JSON, nullable=False, default=lambda: {})
