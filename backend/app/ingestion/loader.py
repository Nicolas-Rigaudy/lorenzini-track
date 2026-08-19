"""Source-agnostic loader for occurrence data.

Ingestion is split into two halves so we can support many data formats, not just the
OBIS-SEAMAP Darwin Core Archives:

  * a *reader* (e.g. `stat_archive`, or a future Movebank / GBIF / CSV reader) knows how to
    fetch a particular source and turn it into a `StudyMetadata` plus a list of
    `NormalizedOccurrence` records, then calls `load(...)`.
  * this *loader* knows how to upsert that normalized shape into the database, and is shared
    by every reader.

To add a new source, write a reader that produces the two shapes below and calls `load`.
"""

from datetime import date, datetime
from typing import TypedDict

from app.core.db import SessionLocal
from app.models.occurrence import Occurrence
from app.models.study import Study


class StudyMetadata(TypedDict, total=False):
    dataset_id: str  # required — stable identifier used for study upsert
    title: str
    abstract: str | None
    data_provider: str | None
    source_url: str | None
    license: str | None
    published_date: date | None


class NormalizedOccurrence(TypedDict, total=False):
    occurrence_id: str  # required — stable identifier used for occurrence upsert
    decimal_latitude: float  # required
    decimal_longitude: float  # required
    dataset_id: str | None
    dataset_name: str | None
    basis_of_record: str | None
    scientific_name: str | None
    vernacular_name: str | None
    event_date_start: datetime | None
    event_date_end: datetime | None
    coordinate_uncertainty_in_meters: float | None
    individual_count: int | None
    sex: str | None
    life_stage: str | None
    occurrence_status: str | None
    organism_id: str | None
    license: str | None
    rights_holder: str | None
    bibliographic_citation: str | None


def upsert_study(metadata: StudyMetadata, rights_holder: str | None) -> Study:
    db = SessionLocal()
    try:
        study = (
            db.query(Study).filter(Study.dataset_id == metadata["dataset_id"]).one_or_none()
        ) or Study(dataset_id=metadata["dataset_id"])

        study.title = metadata.get("title") or ""
        study.abstract = metadata.get("abstract")
        study.data_provider = metadata.get("data_provider")
        study.source_url = metadata.get("source_url")
        study.license = metadata.get("license")
        study.rights_holder = rights_holder
        study.published_date = metadata.get("published_date")

        db.add(study)
        db.commit()
        db.refresh(study)
        return study
    finally:
        db.close()


def upsert_occurrences(records: list[NormalizedOccurrence], study_id: int) -> int:
    db = SessionLocal()
    count = 0
    try:
        for rec in records:
            existing = (
                db.query(Occurrence)
                .filter(Occurrence.occurrence_id == rec["occurrence_id"])
                .one_or_none()
            )
            occurrence = existing or Occurrence(occurrence_id=rec["occurrence_id"])

            occurrence.study_id = study_id
            occurrence.dataset_id = rec.get("dataset_id")
            occurrence.dataset_name = rec.get("dataset_name")
            occurrence.basis_of_record = rec.get("basis_of_record")
            occurrence.scientific_name = rec.get("scientific_name")
            occurrence.vernacular_name = rec.get("vernacular_name")
            occurrence.event_date_start = rec.get("event_date_start")
            occurrence.event_date_end = rec.get("event_date_end")
            occurrence.decimal_latitude = rec["decimal_latitude"]
            occurrence.decimal_longitude = rec["decimal_longitude"]
            occurrence.coordinate_uncertainty_in_meters = rec.get(
                "coordinate_uncertainty_in_meters"
            )
            occurrence.individual_count = rec.get("individual_count")
            occurrence.sex = rec.get("sex")
            occurrence.life_stage = rec.get("life_stage")
            occurrence.occurrence_status = rec.get("occurrence_status")
            occurrence.organism_id = rec.get("organism_id")
            occurrence.license = rec.get("license")
            occurrence.rights_holder = rec.get("rights_holder")
            occurrence.bibliographic_citation = rec.get("bibliographic_citation")
            occurrence.geom = (
                f"SRID=4326;POINT({rec['decimal_longitude']} {rec['decimal_latitude']})"
            )

            db.add(occurrence)
            count += 1

        db.commit()
    finally:
        db.close()

    return count


def load(
    metadata: StudyMetadata, rights_holder: str | None, records: list[NormalizedOccurrence]
) -> Study:
    """Upsert a study and its occurrences. The single entry point every reader calls."""
    study = upsert_study(metadata, rights_holder)
    print(f"Upserted study: {study.title!r} (id={study.id})")
    count = upsert_occurrences(records, study.id)
    print(f"Upserted {count} records into the occurrence table.")
    return study
