"""Ingest the Galapagos basking shark tracking dataset.

Source: OBIS-SEAMAP dataset 1209, STAT-originated Darwin Core Archive. A second
basking shark (Cetorhinus maximus) study, in a different region from the Manx dataset,
to exercise the multiple-studies-per-species UX.
Run directly: python -m app.ingestion.gbif_basking_shark_galapagos
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1209_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
