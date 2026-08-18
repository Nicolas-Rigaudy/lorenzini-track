"""Ingest the giant devil ray tracking dataset (precise, per-fix positions).

Source: OBIS-SEAMAP dataset 1370, "Giant Devil Rays in the North-Western Mediterranean Sea",
non-aggregated Darwin Core Archive (~298 precise points). Adds a ray (Mobula mobular) with
real track resolution rather than 1-degree grid cells.
Run directly: python -m app.ingestion.gbif_devil_ray
"""

from app.ingestion.stat_archive import ingest

ARCHIVE_URL = "https://ipt.env.duke.edu/archive.do?r=zd_1370"

if __name__ == "__main__":
    ingest(ARCHIVE_URL)
