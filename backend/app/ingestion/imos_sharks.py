"""Ingest notable sharks from the IMOS Animal Tracking Facility acoustic dataset.

Source: IMOS ATF Acoustic Tracking (2007-2021), a Darwin Core Archive published by CSIRO.
The archive is large (~83MB zip, 561MB / 1.5M-row occurrence.txt), so we STREAM it: rows are
read one at a time, filtered to a curated set of well-known shark species, and bulk-inserted
in chunks via the shared loader — never holding the whole file in memory.

Coordinates are acoustic receiver-station positions (~1-10km resolution), so tracks are coarse
"which stations an animal visited" paths rather than fine-scale movement.

Run: python -m app.ingestion.imos_sharks
"""

import csv
import io
import os
import tempfile
import zipfile
from datetime import datetime

import httpx

from app.ingestion.loader import NormalizedOccurrence, StudyMetadata, load

ARCHIVE_URL = "https://www.marine.csiro.au/ipt/archive.do?r=imos_atf_ad"

# Curated, well-known shark species to feature (binomial -> common name). scientificName in
# the archive may carry authorship, so we match on the leading "Genus species".
TARGET_SPECIES = {
    "Galeocerdo cuvier": "Tiger shark",
    "Carcharhinus leucas": "Bull shark",
    "Carcharhinus amblyrhynchos": "Grey reef shark",
    "Carcharhinus melanopterus": "Blacktip reef shark",
    "Negaprion acutidens": "Sicklefin lemon shark",
    "Triaenodon obesus": "Whitetip reef shark",
}

METADATA: StudyMetadata = {
    "dataset_id": "imos_atf_ad",
    "title": "IMOS Animal Tracking Facility — Acoustic Tracking (2007–2021)",
    "abstract": (
        "Quality-controlled acoustic telemetry detections of tagged marine animals from "
        "Australia's Integrated Marine Observing System (IMOS) Animal Tracking Facility. "
        "Positions are acoustic receiver-station locations. This study loads a selection of "
        "well-known shark species from the archive."
    ),
    "data_provider": "IMOS Animal Tracking Facility",
    "source_url": "https://www.gbif.org/dataset/3f4d4bf1-5f9a-43f2-a0d8-ff6ed5952796",
    "license": "CC-BY 4.0",
    "published_date": None,
}


def _download(url: str, attempts: int = 5) -> str:
    """Download to a temp file, retrying until we get a complete, valid zip (the source
    server intermittently drops the large transfer mid-stream)."""
    last: Exception | None = None
    for i in range(attempts):
        path = None
        try:
            with httpx.stream("GET", url, follow_redirects=True, timeout=600.0) as r:
                r.raise_for_status()
                with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
                    path = tmp.name
                    for chunk in r.iter_bytes(1 << 16):
                        tmp.write(chunk)
            with zipfile.ZipFile(path) as z:
                if "occurrence.txt" in z.namelist():
                    return path
            raise RuntimeError("occurrence.txt missing")
        except Exception as e:  # noqa: BLE001 - retrying any transient failure
            last = e
            print(f"  download attempt {i + 1}/{attempts} failed: {e}")
            if path and os.path.exists(path):
                os.remove(path)
    raise RuntimeError(f"could not download {url}: {last}")


def _parse_dt(raw: str | None) -> datetime | None:
    if not raw:
        return None
    raw = raw.split("/")[0].strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(raw[:19], fmt)
            except ValueError:
                continue
    return None


def _records(path: str):
    kept = 0
    with zipfile.ZipFile(path) as z, z.open("occurrence.txt") as fh:
        reader = csv.DictReader(
            io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t"
        )
        for i, row in enumerate(reader):
            binomial = " ".join((row.get("scientificName") or "").split()[:2])
            common = TARGET_SPECIES.get(binomial)
            if common is None:
                continue
            lat, lon = row.get("decimalLatitude"), row.get("decimalLongitude")
            if not lat or not lon:
                continue
            try:
                latf, lonf = float(lat), float(lon)
            except ValueError:
                continue
            ts = _parse_dt(row.get("eventDate"))
            rec: NormalizedOccurrence = {
                "occurrence_id": row.get("occurrenceID") or f"imos_atf_ad:{i}",
                "dataset_id": "imos_atf_ad",
                "dataset_name": METADATA["title"],
                "basis_of_record": "MachineObservation",
                "scientific_name": binomial,
                "vernacular_name": common,
                "event_date_start": ts,
                "event_date_end": ts,
                "decimal_latitude": latf,
                "decimal_longitude": lonf,
                "coordinate_uncertainty_in_meters": None,
                "organism_id": row.get("organismID") or None,
                "license": METADATA["license"],
                "rights_holder": row.get("rightsHolder"),
            }
            kept += 1
            yield rec
    print(f"  kept {kept} rows matching target species.")


def main() -> None:
    print(f"Downloading IMOS archive from {ARCHIVE_URL} ...")
    path = _download(ARCHIVE_URL)
    try:
        print("Streaming + filtering to target shark species ...")
        load(METADATA, None, _records(path))
    finally:
        os.remove(path)


if __name__ == "__main__":
    main()
