"""Ingest grey seal GPS telemetry (Molene Archipelago).

Source: OBIS-SEAMAP dataset 2028, non-aggregated Darwin Core Archive (precise per-fix,
~139k points, 21 individuals). Adds a pinniped (Halichoerus grypus) with rich tracks.
Run: python -m app.ingestion.gbif_grey_seal
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_2028"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
