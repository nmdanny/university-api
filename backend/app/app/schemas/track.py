from .common import ExtraData, Translations, ExtraDataField, TranslationsField
from pydantic import BaseModel, Field
from app.db.base import DegreeType


class Track(BaseModel):
    """ A track within a university is usually a path to getting a degree
        Most tracks belong to a particular department & faculty,
        but some tracks can cross departments or even faculties.
    """

    id: str = Field(..., description="Uniquely identifies a track within a university")
    university_id: int
    degree: DegreeType = Field(
        ..., description="Type of academic degree granted upon finishing this track"
    )
    name_translations: Translations = TranslationsField
    extra_data: ExtraData = ExtraDataField

    class Config:
        orm_mode = True
