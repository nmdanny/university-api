from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import literal, select, null, cast, Integer
from sqlalchemy.orm import with_polymorphic, aliased
from sqlalchemy.sql import column, label

from app import models, schemas
from app.api import deps

router = APIRouter()

@router.get("/", response_model=List[schemas.Track])
def read_tracks(
    university_id: int,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    tracks = (
        db.query(models.Track)
        .filter(models.Track.university_id == university_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return tracks


@router.get("/{track_id}", response_model=schemas.Track)
def read_track(
    university_id: int, track_id: str, db: Session = Depends(deps.get_db),
) -> Any:
    track = (
        db.query(models.Track)
        .filter(
            (models.Track.university_id == university_id)
            & (models.Track.id == track_id)
        )
        .first()
    )
    if not track:
        raise HTTPException(status_code=404)
    return track


@router.get("/{track_id}/dag", response_model=List[Any])
def get_track_dag(
    university_id: int,
    track_id: str,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """ Returns all nodes in the DAG of given track, along with their parent and distance
        from root. Nodes which have multiple parents appear multiple times
    """

    rec_base = (
        db.query(
            models.DAGNode,
            literal(0).label("distance"),
            cast(null(), Integer).label("parent_id"),
        )
        .filter(
            (models.DAGRootNode.university_id == university_id)
            & (models.DAGRootNode.track_id == track_id)
            & (models.DAGNode.node_type == "DAGRootNode")
        )
        .cte(name="descendants", recursive=True)
    )

    parent = aliased(rec_base, name="parent")
    child = aliased(models.DAGNode, name="child")

    rec_base = rec_base.union_all(
        db.query(child, parent.c.distance + 1, parent.c.node_id)
        .join(child, models.DAGNode.children)
        .filter(
            (parent.c.distance <= 10) & (models.DAGNode.node_id == parent.c.node_id)
        )
    )

    result = db.query(rec_base).all()

    if not result:
        raise HTTPException(status_code=404)
    return result
