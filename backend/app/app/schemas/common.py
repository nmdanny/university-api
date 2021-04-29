from typing import Dict, Any, Optional
from pydantic import Field

ExtraData = Optional[Dict[str, Any]]
Translations = Dict[str, str]

ExtraDataField: ExtraData = Field(
    None, description="An object containing extra, university-specific data for some entity"
)

TranslationsField: Translations = Field(
    ..., description="Maps 2 letter language codes to their respective translations",
    example='{ "en": "Databases", "he": "מסדי נתונים" }'
)
