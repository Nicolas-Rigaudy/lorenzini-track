from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Integer, cast, extract, func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.data.species_facts import SPECIES_FACTS
from app.models.occurrence import Occurrence
from app.models.study import Study

router = APIRouter(prefix="/species", tags=["species"])


def _base_stats(db: Session, scientific_name: str) -> dict:
    row = db.execute(
        select(
            func.count(Occurrence.id),
            func.count(func.distinct(Occurrence.study_id)),
            func.min(Occurrence.event_date_start),
            func.max(Occurrence.event_date_end),
            func.max(Occurrence.vernacular_name),
        ).where(Occurrence.scientific_name == scientific_name)
    ).one()
    record_count, study_count, date_start, date_end, vernacular = row
    return {
        "scientific_name": scientific_name,
        "vernacular_name": vernacular,
        "record_count": record_count,
        "study_count": study_count,
        "date_range": {
            "start": date_start.isoformat() if date_start else None,
            "end": date_end.isoformat() if date_end else None,
        },
    }


@router.get("")
def list_species(db: Session = Depends(get_db)) -> list[dict]:
    """Every species present in the occurrence data, with counts and curated facts.

    Drives the species gallery. Kept lean: image/description/IUCN are fetched client-side
    from Wikipedia, so they are intentionally not returned here.
    """
    names = (
        db.execute(
            select(Occurrence.scientific_name)
            .where(Occurrence.scientific_name.is_not(None))
            .distinct()
            .order_by(Occurrence.scientific_name)
        )
        .scalars()
        .all()
    )

    result = []
    for name in names:
        facts = SPECIES_FACTS.get(name, {})
        result.append(
            {
                **_base_stats(db, name),
                "common_name": facts.get("common_name"),
                "body_plan": facts.get("body_plan"),
            }
        )
    return result


@router.get("/{scientific_name:path}")
def get_species(scientific_name: str, db: Session = Depends(get_db)) -> dict:
    """Full learning-resource profile: curated facts + stats + a monthly detection histogram."""
    stats = _base_stats(db, scientific_name)
    if stats["record_count"] == 0 and scientific_name not in SPECIES_FACTS:
        raise HTTPException(status_code=404, detail="Species not found")

    # Seasonal histogram: occurrence counts bucketed by calendar month (1-12), so the
    # profile can show when this species is detected across the year.
    month_rows = db.execute(
        select(
            cast(extract("month", Occurrence.event_date_start), Integer),
            func.count(Occurrence.id),
        )
        .where(
            Occurrence.scientific_name == scientific_name,
            Occurrence.event_date_start.is_not(None),
        )
        .group_by(cast(extract("month", Occurrence.event_date_start), Integer))
    ).all()
    by_month = {month: count for month, count in month_rows}
    histogram = [by_month.get(m, 0) for m in range(1, 13)]

    # Records per calendar year, for the "by year" chart.
    year_rows = db.execute(
        select(
            cast(extract("year", Occurrence.event_date_start), Integer),
            func.count(Occurrence.id),
        )
        .where(
            Occurrence.scientific_name == scientific_name,
            Occurrence.event_date_start.is_not(None),
        )
        .group_by(cast(extract("year", Occurrence.event_date_start), Integer))
        .order_by(cast(extract("year", Occurrence.event_date_start), Integer))
    ).all()
    yearly_histogram = [{"year": year, "count": count} for year, count in year_rows]

    # Distinct tagged individuals (organismID), where the source provides it.
    tag_count = db.execute(
        select(func.count(func.distinct(Occurrence.organism_id))).where(
            Occurrence.scientific_name == scientific_name,
            Occurrence.organism_id.is_not(None),
        )
    ).scalar_one()

    study_ids = (
        db.execute(
            select(func.distinct(Occurrence.study_id))
            .where(
                Occurrence.scientific_name == scientific_name,
                Occurrence.study_id.is_not(None),
            )
            .join(Study, Study.id == Occurrence.study_id)
        )
        .scalars()
        .all()
    )

    return {
        **stats,
        "facts": SPECIES_FACTS.get(scientific_name),
        "monthly_histogram": histogram,
        "yearly_histogram": yearly_histogram,
        "tag_count": tag_count,
        "study_ids": study_ids,
    }
