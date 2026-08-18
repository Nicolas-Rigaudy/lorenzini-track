"""Ingest the Western Caribbean & Gulf of Mexico whale shark & manta aggregations dataset.

Source: OBIS-SEAMAP dataset 594 (MarAlliance), STAT-originated Darwin Core Archive.
Adds the first ray (Manta birostris) to the platform; also contributes additional whale
shark (Rhincodon typus) occurrences. See docs/decisions/0006 for the ingestion pattern.
Run directly: python -m app.ingestion.gbif_manta
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_594_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
