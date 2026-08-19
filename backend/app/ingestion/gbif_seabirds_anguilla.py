"""Ingest University of Liverpool seabird tracking in Anguilla (2012-2015).

Source: OBIS-SEAMAP dataset 1279, non-aggregated Darwin Core Archive (~270k points,
247 individuals). Adds three seabird species: brown booby (Sula leucogaster), magnificent
frigatebird (Fregata magnificens), masked booby (Sula dactylatra).
Run: python -m app.ingestion.gbif_seabirds_anguilla
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1279"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
