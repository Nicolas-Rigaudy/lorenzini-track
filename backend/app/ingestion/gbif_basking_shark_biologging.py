"""Ingest the basking shark long-term biologging dataset (precise, per-fix positions).

Source: OBIS-SEAMAP dataset 2383, non-aggregated Darwin Core Archive — unlike the 1-degree
aggregated datasets, this holds precise individual telemetry fixes (~1,468 points), so it
renders as real tracks rather than a grid.
Run directly: python -m app.ingestion.gbif_basking_shark_biologging
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_2383"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
