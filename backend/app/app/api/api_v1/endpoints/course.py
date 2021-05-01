from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.Course])
def read_courses(
    university_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    courses = (
        db.query(models.Course)
        .filter(models.Course.university_id == university_id)
        .join(models.Term)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return courses


@router.get("/{course_id}", response_model=schemas.Course)
def read_course(
    university_id: int, course_id: str, db: Session = Depends(deps.get_db),
) -> Any:
    course = (
        db.query(models.Course)
        .filter(
            (models.Course.university_id == university_id)
            & (models.Course.id == course_id)
        )
        .first()
    )
    if not course:
        raise HTTPException(status_code=404)
    return course
