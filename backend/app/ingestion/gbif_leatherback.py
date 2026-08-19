"""Ingest leatherback turtle telemetry.

Source: OBIS-SEAMAP dataset 439, Darwin Core Archive (~3.6k points, 9 individuals, precise).
Adds a second reptile (Dermochelys coriacea).
Run: python -m app.ingestion.gbif_leatherback
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_439"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
