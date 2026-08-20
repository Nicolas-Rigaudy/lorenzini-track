from math import ceil

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.occurrence import Occurrence

router = APIRouter(tags=["occurrences"])

# Point caps keep payloads small and the map fast. A selected species is evenly down-sampled
# to at most MAX_POINTS (plenty for a dense map, and far faster than shipping 100k+ points);
# a whole multi-species study keeps up to PER_SPECIES_OVERVIEW per species.
MAX_POINTS = 20000
PER_SPECIES_OVERVIEW = 2500

_FIELDS = (
    Occurrence.occurrence_id,
    Occurrence.study_id,
    Occurrence.organism_id,
    Occurrence.scientific_name,
    Occurrence.vernacular_name,
    Occurrence.event_date_start,
    Occurrence.event_date_end,
    Occurrence.decimal_latitude,
    Occurrence.decimal_longitude,
    Occurrence.coordinate_uncertainty_in_meters,
    Occurrence.individual_count,
    Occurrence.sex,
    Occurrence.life_stage,
    Occurrence.occurrence_status,
    Occurrence.license,
    Occurrence.rights_holder,
)


def _feature(row) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [row.decimal_longitude, row.decimal_latitude]},
        "properties": {
            "occurrence_id": row.occurrence_id,
            "study_id": row.study_id,
            "organism_id": row.organism_id,
            "scientific_name": row.scientific_name,
            "vernacular_name": row.vernacular_name,
            "event_date_start": row.event_date_start.isoformat() if row.event_date_start else None,
            "event_date_end": row.event_date_end.isoformat() if row.event_date_end else None,
            "coordinate_uncertainty_in_meters": row.coordinate_uncertainty_in_meters,
            "individual_count": row.individual_count,
            "sex": row.sex,
            "life_stage": row.life_stage,
            "occurrence_status": row.occurrence_status,
            "license": row.license,
            "rights_holder": row.rights_holder,
        },
    }


@router.get("/occurrences")
def list_occurrences(
    study_id: int | None = None,
    scientific_name: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    filters = []
    if study_id is not None:
        filters.append(Occurrence.study_id == study_id)
    if scientific_name is not None:
        filters.append(Occurrence.scientific_name == scientific_name)

    total = db.execute(select(func.count(Occurrence.id)).where(*filters)).scalar_one()

    if scientific_name is not None:
        # A selected species: even id-strided sample capped at MAX_POINTS for a fast map.
        if total > MAX_POINTS:
            stride = ceil(total / MAX_POINTS)
            query = select(*_FIELDS).where(*filters, Occurrence.id % stride == 0)
            sampled = True
        else:
            query = select(*_FIELDS).where(*filters)
            sampled = False
        rows = db.execute(query).all()
    else:
        # A whole multi-species study (or the unfiltered fallback): keep up to
        # PER_SPECIES_OVERVIEW points of each species so one huge species doesn't drown out
        # the rest and the payload stays manageable.
        rn = func.row_number().over(
            partition_by=Occurrence.scientific_name, order_by=Occurrence.id
        )
        sub = select(*_FIELDS, rn.label("rn")).where(*filters).subquery()
        query = select(sub).where(sub.c.rn <= PER_SPECIES_OVERVIEW)
        rows = db.execute(query).all()
        sampled = len(rows) < total

    return {
        "type": "FeatureCollection",
        "total": total,
        "returned": len(rows),
        "sampled": sampled,
        "features": [_feature(r) for r in rows],
    }
