"""Ingest an additional Ningaloo Outlook whale shark tracking dataset.

Source: OBIS-SEAMAP dataset 1296, STAT-originated Darwin Core Archive. A second whale
shark (Rhincodon typus) study alongside dataset 1298, to exercise the
multiple-studies-per-species UX.
Run directly: python -m app.ingestion.gbif_whale_shark_1296
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1296_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
