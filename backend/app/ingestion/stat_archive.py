"""Reader for OBIS-SEAMAP / GBIF Darwin Core Archives (the STAT-originated pattern behind our
shark and ray datasets; see docs/decisions/0002 and 0006).

This module only knows how to *read* a Darwin Core Archive and normalise it; the database
upsert lives in `app.ingestion.loader`, shared with any other source reader.

Note: the `_1deg` variants are aggregated per species per 1-degree grid cell (so
coordinateUncertaintyInMeters ~111km reflects cell size); the non-suffixed variants are
precise per-fix positions.
"""

import csv
import io
import re
import zipfile
from datetime import date, datetime
from xml.etree import ElementTree

import httpx

from app.ingestion.loader import NormalizedOccurrence, StudyMetadata, load


def _parse_event_date(raw: str) -> tuple[datetime | None, datetime | None]:
    """eventDate is an ISO 8601 interval, e.g. '2015-08-02T09:06:22/2015-08-06T07:43:02'."""
    if not raw:
        return None, None
    parts = raw.split("/")
    start = datetime.fromisoformat(parts[0])
    end = datetime.fromisoformat(parts[1]) if len(parts) > 1 else start
    return start, end


def _parse_study_metadata(eml_bytes: bytes, dataset_id: str) -> StudyMetadata:
    root = ElementTree.fromstring(eml_bytes)
    dataset_el = root.find(".//dataset")

    title = dataset_el.findtext("title", default="").strip()
    abstract_para = dataset_el.findtext("abstract/para", default="")
    abstract_para = re.sub(r"<[^>]+>", "", abstract_para)  # strip embedded HTML (e.g. <a> links)

    # The raw text mixes a "Original provider / Dataset credits" preamble with the actual
    # research abstract under an "Abstract:" heading - split them so the UI can show the real
    # abstract on its own, and pull out the data provider name as a separate field.
    abstract_section = abstract_para.split("Abstract:", 1)
    abstract = re.sub(r"\s+", " ", abstract_section[-1]).strip() or None if abstract_section[-1] else None

    data_provider_match = re.search(r"Data provider\s*\n\s*([^\n]+)", abstract_para)
    data_provider = data_provider_match.group(1).strip() if data_provider_match else None

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
        "data_provider": data_provider,
        "source_url": source_url,
        "license": rights_text or None,
        "published_date": published_date,
    }


def fetch_archive(archive_url: str) -> tuple[list[dict], bytes]:
    response = httpx.get(archive_url, follow_redirects=True, timeout=30.0)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        with archive.open("occurrence.txt") as f:
            reader = csv.DictReader(io.TextIOWrapper(f, encoding="utf-8"), delimiter="\t")
            records = list(reader)
        eml_bytes = archive.read("eml.xml")

    return records, eml_bytes


def _to_float(value: str | None) -> float | None:
    return float(value) if value else None


def _to_int(value: str | None) -> int | None:
    return int(value) if value else None


def _to_normalized(row: dict) -> NormalizedOccurrence:
    """Map a Darwin Core occurrence row to the loader's normalized shape."""
    event_start, event_end = _parse_event_date(row.get("eventDate", ""))
    return {
        "occurrence_id": row["occurrenceID"],
        "dataset_id": row.get("datasetID"),
        "dataset_name": row.get("datasetName"),
        "basis_of_record": row.get("basisOfRecord"),
        "scientific_name": row.get("scientificName"),
        "vernacular_name": row.get("vernacularName"),
        "event_date_start": event_start,
        "event_date_end": event_end,
        "decimal_latitude": float(row["decimalLatitude"]),
        "decimal_longitude": float(row["decimalLongitude"]),
        "coordinate_uncertainty_in_meters": _to_float(row.get("coordinateUncertaintyInMeters")),
        "individual_count": _to_int(row.get("individualCount")),
        "sex": row.get("sex"),
        "life_stage": row.get("lifeStage"),
        "occurrence_status": row.get("occurrenceStatus"),
        "organism_id": row.get("organismID"),
        "license": row.get("license"),
        "rights_holder": row.get("rightsHolder"),
        "bibliographic_citation": row.get("bibliographicCitation"),
    }


def ingest(archive_url: str) -> None:
    print(f"Fetching Darwin Core Archive from {archive_url} ...")
    records, eml_bytes = fetch_archive(archive_url)
    print(f"Parsed {len(records)} occurrence records.")

    dataset_id = records[0]["datasetID"] if records else ""
    rights_holder = records[0].get("rightsHolder") if records else None
    metadata = _parse_study_metadata(eml_bytes, dataset_id)
    load(metadata, rights_holder, [_to_normalized(r) for r in records])
