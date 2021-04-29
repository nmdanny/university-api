from .common import ExtraData, Translations, ExtraDataField, TranslationsField
from pydantic import BaseModel, Field


class Term(BaseModel):
    """ A term is a period of an academic year in which a course is held.
        Some universities may use semesters(2 terms in a year), some might use
        trimesters and so on. There might also be special kinds of terms, like a
        whole-year course, or a special summer course and so on.

        A term in the database does not have a clear scheduling. For example, if we have
        terms for 'Semester 1' and 'Semester 2', it's likely they will represent
        different dates between universities of different countries, or
        even within the same country.
    """

    id: int = Field(..., description="Uniquely identifies a term")
    name_translations: Translations = TranslationsField

    class Config:
        orm_mode = True


class Course(BaseModel):
    """ A course belongs to a university, and can be associated to
        various tracks(and indirectly, to various departments/faculties)
    """

    id: str = Field(..., description="Uniquely identifies a course within a university")
    university_id: int
    name_translations: Translations = TranslationsField
    extra_data: ExtraData = ExtraDataField
    term: Term
    course_credits: int = Field(
        ..., description="Number of academic credits for the course"
    )

    class Config:
        orm_mode = True
