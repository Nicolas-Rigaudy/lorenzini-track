from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.occurrence import Occurrence
from app.models.study import Study

router = APIRouter(prefix="/studies", tags=["studies"])


def _summarize(db: Session, study: Study) -> dict:
    stats = db.execute(
        select(
            func.count(Occurrence.id),
            func.min(Occurrence.event_date_start),
            func.max(Occurrence.event_date_end),
            func.array_agg(func.distinct(Occurrence.scientific_name)),
        ).where(Occurrence.study_id == study.id)
    ).one()
    record_count, date_start, date_end, species = stats

    return {
        "id": study.id,
        "dataset_id": study.dataset_id,
        "title": study.title,
        "abstract": study.abstract,
        "source_url": study.source_url,
        "license": study.license,
        "rights_holder": study.rights_holder,
        "published_date": study.published_date.isoformat() if study.published_date else None,
        "record_count": record_count,
        "date_range": {
            "start": date_start.isoformat() if date_start else None,
            "end": date_end.isoformat() if date_end else None,
        },
        "species": [s for s in species if s] if species else [],
    }


@router.get("")
def list_studies(db: Session = Depends(get_db)) -> list[dict]:
    studies = db.execute(select(Study)).scalars().all()
    return [_summarize(db, study) for study in studies]


@router.get("/{study_id}")
def get_study(study_id: int, db: Session = Depends(get_db)) -> dict:
    study = db.get(Study, study_id)
    if study is None:
        raise HTTPException(status_code=404, detail="Study not found")
    return _summarize(db, study)
