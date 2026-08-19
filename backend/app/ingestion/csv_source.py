"""Reader for generic tabular tracking data (CSV) — e.g. Movebank exports, OCEARCH/NOAA
downloads, or any per-fix CSV.

Unlike `stat_archive` (Darwin Core Archives), this reads a flat CSV whose columns you map to
the normalized fields. Defaults match Movebank's column names. It builds one occurrence per
row and delegates the database upsert to `app.ingestion.loader`.

Example:
    from app.ingestion.csv_source import ingest_csv
    ingest_csv(
        "https://example.org/tracks.csv",
        metadata={"dataset_id": "mb-123", "title": "Tiger sharks off Hawaii",
                  "source_url": "https://www.movebank.org/...", "license": "CC-BY-NC 4.0"},
        rights_holder="Some Lab",
    )
"""

import csv
import io
from datetime import datetime

import httpx

from app.ingestion.loader import NormalizedOccurrence, StudyMetadata, load

# normalized field -> source CSV column (Movebank defaults)
DEFAULT_MAPPING: dict[str, str] = {
    "decimal_latitude": "location-lat",
    "decimal_longitude": "location-long",
    "timestamp": "timestamp",
    "organism_id": "individual-local-identifier",
    "scientific_name": "individual-taxon-canonical-name",
    "occurrence_id": "event-id",
}


def _fetch_rows(source: str) -> list[dict]:
    if source.startswith("http://") or source.startswith("https://"):
        resp = httpx.get(source, follow_redirects=True, timeout=60.0)
        resp.raise_for_status()
        text = resp.text
    else:
        with open(source, encoding="utf-8") as f:
            text = f.read()
    return list(csv.DictReader(io.StringIO(text)))


def _parse_timestamp(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.strip())
    except ValueError:
        # Fall back to a few common non-ISO layouts before giving up.
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw.strip(), fmt)
            except ValueError:
                continue
    return None


def ingest_csv(
    source: str,
    metadata: StudyMetadata,
    rights_holder: str | None = None,
    mapping: dict[str, str] | None = None,
) -> None:
    """Ingest a CSV of per-fix records. `source` is a URL or local path."""
    cols = {**DEFAULT_MAPPING, **(mapping or {})}
    print(f"Fetching CSV from {source} ...")
    rows = _fetch_rows(source)
    print(f"Parsed {len(rows)} rows.")

    dataset_id = metadata["dataset_id"]
    records: list[NormalizedOccurrence] = []
    for i, row in enumerate(rows):
        lat, lon = row.get(cols["decimal_latitude"]), row.get(cols["decimal_longitude"])
        if not lat or not lon:
            continue  # skip rows without a position
        ts = _parse_timestamp(row.get(cols["timestamp"]))
        occ_id = row.get(cols["occurrence_id"]) or f"{dataset_id}:{i}"
        records.append(
            {
                "occurrence_id": occ_id,
                "dataset_id": dataset_id,
                "dataset_name": metadata.get("title"),
                "basis_of_record": "MachineObservation",
                "scientific_name": row.get(cols["scientific_name"]),
                "event_date_start": ts,
                "event_date_end": ts,
                "decimal_latitude": float(lat),
                "decimal_longitude": float(lon),
                "organism_id": row.get(cols["organism_id"]),
                "license": metadata.get("license"),
                "rights_holder": rights_holder,
            }
        )

    load(metadata, rights_holder, records)
