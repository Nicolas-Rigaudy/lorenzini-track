"""Ingest the Ningaloo Outlook Whale Shark tracking dataset (GBIF-published, 1-degree-cell
aggregated) into the occurrence table.

Source: GBIF dataset 1c61952a-9c15-48cc-b3c4-f3d541e45ab2, Darwin Core Archive.
See docs/decisions/0002-flagship-track-dataset.md for why this specific dataset was chosen.

Note: records are aggregated per species per 1-degree grid cell and time window (not raw
per-fix telemetry positions) - coordinateUncertaintyInMeters (~111km) reflects that cell size,
not GPS/Argos accuracy. Run directly: python -m app.ingestion.gbif_whale_sharks
"""

import csv
import io
import zipfile
from datetime import datetime

import httpx

from app.core.db import SessionLocal
from app.models.occurrence import Occurrence

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1298_1deg"


def _parse_event_date(raw: str) -> tuple[datetime | None, datetime | None]:
    """eventDate is an ISO 8601 interval, e.g. '2015-08-02T09:06:22/2015-08-06T07:43:02'."""
    if not raw:
        return None, None
    parts = raw.split("/")
    start = datetime.fromisoformat(parts[0])
    end = datetime.fromisoformat(parts[1]) if len(parts) > 1 else start
    return start, end


def fetch_records() -> list[dict]:
    response = httpx.get(ARCHIVE_URL, follow_redirects=True, timeout=30.0)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        with archive.open("occurrence.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t")
            return list(reader)


def upsert_records(records: list[dict]) -> int:
    db = SessionLocal()
    count = 0
    try:
        for row in records:
            event_start, event_end = _parse_event_date(row.get("eventDate", ""))
            lat = float(row["decimalLatitude"])
            lon = float(row["decimalLongitude"])

            existing = (
                db.query(Occurrence)
                .filter(Occurrence.occurrence_id == row["occurrenceID"])
                .one_or_none()
            )
            occurrence = existing or Occurrence(occurrence_id=row["occurrenceID"])

            occurrence.dataset_id = row.get("datasetID")
            occurrence.dataset_name = row.get("datasetName")
            occurrence.basis_of_record = row.get("basisOfRecord")
            occurrence.scientific_name = row.get("scientificName")
            occurrence.vernacular_name = row.get("vernacularName")
            occurrence.event_date_start = event_start
            occurrence.event_date_end = event_end
            occurrence.decimal_latitude = lat
            occurrence.decimal_longitude = lon
            occurrence.coordinate_uncertainty_in_meters = _to_float(
                row.get("coordinateUncertaintyInMeters")
            )
            occurrence.individual_count = _to_int(row.get("individualCount"))
            occurrence.sex = row.get("sex")
            occurrence.life_stage = row.get("lifeStage")
            occurrence.occurrence_status = row.get("occurrenceStatus")
            occurrence.organism_id = row.get("organismID")
            occurrence.license = row.get("license")
            occurrence.rights_holder = row.get("rightsHolder")
            occurrence.bibliographic_citation = row.get("bibliographicCitation")
            occurrence.geom = f"SRID=4326;POINT({lon} {lat})"

            db.add(occurrence)
            count += 1

        db.commit()
    finally:
        db.close()

    return count


def _to_float(value: str | None) -> float | None:
    return float(value) if value else None


def _to_int(value: str | None) -> int | None:
    return int(value) if value else None


def main() -> None:
    print(f"Fetching Darwin Core Archive from {ARCHIVE_URL} ...")
    records = fetch_records()
    print(f"Parsed {len(records)} occurrence records.")

    count = upsert_records(records)
    print(f"Upserted {count} records into the occurrence table.")


if __name__ == "__main__":
    main()
