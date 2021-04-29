from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Track])
def read_tracks(
    university_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100
) -> Any:
    tracks = db.query(models.Track)\
        .filter(models.Track.university_id == university_id)\
        .offset(skip)\
        .limit(limit)\
        .all()
    return tracks


@router.get("/{track_id}", response_model=schemas.Track)
def read_track(
    university_id: int,
    track_id: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    track = db.query(models.Track)\
        .filter((models.Track.university_id == university_id) &
                (models.Track.id == track_id))\
        .first()
    if not track:
        raise HTTPException(status_code=404)
    return track