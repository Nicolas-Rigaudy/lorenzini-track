from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.occurrence import Occurrence

router = APIRouter(tags=["occurrences"])


@router.get("/occurrences")
def list_occurrences(db: Session = Depends(get_db)) -> dict:
    rows = db.execute(select(Occurrence)).scalars().all()

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
