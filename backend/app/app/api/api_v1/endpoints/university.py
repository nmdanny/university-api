from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.University])
def read_universities(
    db: Session = Depends(deps.get_db), skip: int = 0, limit: int = 100
) -> Any:
    unis = (
        db.query(models.University)
        .options(
            joinedload(models.University.faculties),  # type: ignore
            joinedload(models.University.departments),  # type: ignore
        )
        .offset(skip)
        .limit(limit)
        .all()
    )
    return unis


@router.get("/{university_id}", response_model=schemas.UniversityWithTracks)
def read_university(university_id: int, db: Session = Depends(deps.get_db)) -> Any:

    uni = (
        db.query(models.University)
        .options(
            joinedload(models.University.faculties),  # type: ignore
            joinedload(models.University.departments),  # type: ignore
            joinedload(models.University.tracks),  # type: ignore
        )
        .filter(models.University.id == university_id)
        .first()
    )
    if not uni:
        raise HTTPException(status_code=404)
    return uni
