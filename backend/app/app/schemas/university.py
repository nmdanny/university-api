from typing import List
from .common import ExtraData, Translations, ExtraDataField, TranslationsField
from pydantic import BaseModel, Field
from .track import Track


class Department(BaseModel):
    """ A department(חוג) within a faculty """

    id: str = Field(..., description="An university-specific department identifier")
    university_id: int
    name_translations: Translations = TranslationsField
    extra_data: ExtraData = ExtraDataField

    class Config:
        orm_mode = True


class Faculty(BaseModel):
    """ A faculty/school """

    id: str = Field(..., description="An university-specific faculty identifier")
    university_id: int
    name_translations: Translations = TranslationsField
    extra_data: ExtraData = ExtraDataField

    class Config:
        orm_mode = True


class University(BaseModel):
    """ Identifies a university at a particular point in time(e.g, year) 
        All entities in the API are tied to a university """

    id: int = Field(
        ...,
        description="An identifier assigned by the API to uniquely identify a university at a certain time.",
    )
    name_translations: Translations = TranslationsField
    extra_data: ExtraData = ExtraDataField

    faculties: List[Faculty]
    departments: List[Department]

    class Config:
        orm_mode = True


class UniversityWithTracks(University):
    tracks: List[Track]
