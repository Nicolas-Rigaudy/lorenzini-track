"""Ingest the Ningaloo Outlook Whale Shark tracking dataset (GBIF-published, 1-degree-cell
aggregated) into the study and occurrence tables.

Source: GBIF dataset 1c61952a-9c15-48cc-b3c4-f3d541e45ab2, Darwin Core Archive.
See docs/decisions/0002-flagship-track-dataset.md for why this specific dataset was chosen.

Note: records are aggregated per species per 1-degree grid cell and time window (not raw
per-fix telemetry positions) - coordinateUncertaintyInMeters (~111km) reflects that cell size,
not GPS/Argos accuracy. Run directly: python -m app.ingestion.gbif_whale_sharks
"""

import csv
import io
import re
import zipfile
from datetime import date, datetime
from xml.etree import ElementTree

import httpx

from app.core.db import SessionLocal
from app.models.occurrence import Occurrence
from app.models.study import Study

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1298_1deg"


def _parse_event_date(raw: str) -> tuple[datetime | None, datetime | None]:
    """eventDate is an ISO 8601 interval, e.g. '2015-08-02T09:06:22/2015-08-06T07:43:02'."""
    if not raw:
        return None, None
    parts = raw.split("/")
    start = datetime.fromisoformat(parts[0])
    end = datetime.fromisoformat(parts[1]) if len(parts) > 1 else start
    return start, end


def _parse_study_metadata(eml_bytes: bytes, dataset_id: str) -> dict:
    root = ElementTree.fromstring(eml_bytes)
    dataset_el = root.find(".//dataset")

    title = dataset_el.findtext("title", default="").strip()
    abstract_para = dataset_el.findtext("abstract/para", default="")
    abstract_para = re.sub(r"<[^>]+>", "", abstract_para)  # strip embedded HTML (e.g. <a> links)
    abstract = re.sub(r"\s+", " ", abstract_para).strip() or None
    source_url = dataset_el.findtext("distribution/online/url")
    rights_el = dataset_el.find("intellectualRights/para")
    rights_text = "".join(rights_el.itertext()) if rights_el is not None else ""
    rights_text = re.sub(r"\s+", " ", rights_text).strip()
    published_raw = dataset_el.findtext("pubDate", default="").strip()
    published_date = date.fromisoformat(published_raw) if published_raw else None

    return {
        "dataset_id": dataset_id,
        "title": title,
        "abstract": abstract,
        "source_url": source_url,
        "license": rights_text or None,
        "published_date": published_date,
    }


def fetch_archive() -> tuple[list[dict], bytes]:
    response = httpx.get(ARCHIVE_URL, follow_redirects=True, timeout=30.0)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        with archive.open("occurrence.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t")
            records = list(reader)
        eml_bytes = archive.read("eml.xml")

    return records, eml_bytes


def upsert_study(metadata: dict, rights_holder: str | None) -> Study:
    db = SessionLocal()
    try:
        study = (
            db.query(Study).filter(Study.dataset_id == metadata["dataset_id"]).one_or_none()
        ) or Study(dataset_id=metadata["dataset_id"])

        study.title = metadata["title"]
        study.abstract = metadata["abstract"]
        study.source_url = metadata["source_url"]
        study.license = metadata["license"]
        study.rights_holder = rights_holder
        study.published_date = metadata["published_date"]

        db.add(study)
        db.commit()
        db.refresh(study)
        return study
    finally:
        db.close()


def upsert_records(records: list[dict], study_id: int) -> int:
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

            occurrence.study_id = study_id
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
    records, eml_bytes = fetch_archive()
    print(f"Parsed {len(records)} occurrence records.")

    dataset_id = records[0]["datasetID"] if records else ""
    rights_holder = records[0].get("rightsHolder") if records else None
    metadata = _parse_study_metadata(eml_bytes, dataset_id)
    study = upsert_study(metadata, rights_holder)
    print(f"Upserted study: {study.title!r} (id={study.id})")

    count = upsert_records(records, study.id)
    print(f"Upserted {count} records into the occurrence table.")


if __name__ == "__main__":
    main()
