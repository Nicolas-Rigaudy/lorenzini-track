"""Ingest green sea turtle telemetry (Northwest Costa Rica).

Source: OBIS-SEAMAP dataset 2385, non-aggregated Darwin Core Archive (precise per-fix,
~854 points, 9 individuals). Adds a reptile (Chelonia mydas).
Run: python -m app.ingestion.gbif_green_turtle
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_2385"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
