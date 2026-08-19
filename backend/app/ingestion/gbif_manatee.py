"""Ingest the Florida Manatee Synoptic Aerial Survey (1991-2019).

Source: OBIS-SEAMAP dataset 765, Darwin Core Archive (~16.5k points; aerial survey, so no
per-individual IDs -> shown as points, not tracks). Adds a sirenian (Trichechus manatus).
Run: python -m app.ingestion.gbif_manatee
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_765"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
