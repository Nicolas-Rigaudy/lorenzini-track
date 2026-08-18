"""Ingest the MesoAmerican Reef shark habitat & environmental preferences dataset.

Source: OBIS-SEAMAP dataset 1225 (MarAlliance Sharks and Rays Program), STAT-originated
Darwin Core Archive. Adds lemon shark (Negaprion brevirostris) as a new species.
Run directly: python -m app.ingestion.gbif_lemon_shark
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1225_1deg"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
