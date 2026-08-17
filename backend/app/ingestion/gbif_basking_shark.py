"""Ingest the Manx Basking Shark Watch 2017-2018 tracking dataset.

Source: GBIF dataset 20b89c9f-0a89-4fb6-9dd0-473bba1f656d, Darwin Core Archive.
A second species (Cetorhinus maximus, basking shark) to validate multi-study/multi-species
features (study filtering, species browsing) with more than one real dataset.
Run directly: python -m app.ingestion.gbif_basking_shark
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1512_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
