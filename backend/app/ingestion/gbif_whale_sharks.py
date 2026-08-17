"""Ingest the Ningaloo Outlook Whale Shark tracking dataset.

Source: GBIF dataset 1c61952a-9c15-48cc-b3c4-f3d541e45ab2, Darwin Core Archive.
See docs/decisions/0002-flagship-track-dataset.md for why this dataset was chosen.
Run directly: python -m app.ingestion.gbif_whale_sharks
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1298_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
