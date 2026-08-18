from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.occurrence import Occurrence

router = APIRouter(tags=["occurrences"])


@router.get("/occurrences")
def list_occurrences(
    study_id: int | None = None,
    scientific_name: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = select(Occurrence)
    if study_id is not None:
        query = query.where(Occurrence.study_id == study_id)
    if scientific_name is not None:
        query = query.where(Occurrence.scientific_name == scientific_name)
    rows = db.execute(query).scalars().all()

    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row.decimal_longitude, row.decimal_latitude],
                },
                "properties": {
                    "occurrence_id": row.occurrence_id,
                    "study_id": row.study_id,
                    "organism_id": row.organism_id,
                    "scientific_name": row.scientific_name,
                    "vernacular_name": row.vernacular_name,
                    "event_date_start": row.event_date_start.isoformat()
                    if row.event_date_start
                    else None,
                    "event_date_end": row.event_date_end.isoformat()
                    if row.event_date_end
                    else None,
                    "coordinate_uncertainty_in_meters": row.coordinate_uncertainty_in_meters,
                    "individual_count": row.individual_count,
                    "sex": row.sex,
                    "life_stage": row.life_stage,
                    "occurrence_status": row.occurrence_status,
                    "license": row.license,
                    "rights_holder": row.rights_holder,
                },
            }
            for row in rows
        ],
    }
