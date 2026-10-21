"""Static export (item_005): the files carry what the API serves, and only processed tracks.

Needs the disposable PostGIS that backend/scripts/test.sh starts.
"""

import json

from sqlalchemy import delete

from app.core.db import SessionLocal
from app.export.__main__ import export, slug
from app.ingestion.loader import load
from app.models.occurrence import Occurrence
from app.models.study import Study
from app.models.telemetry import Deployment, SatelliteFixRow, TrackPointRow, TrackSegment


def _clear(session):
    for model in (TrackPointRow, TrackSegment, SatelliteFixRow, Deployment, Occurrence, Study):
        session.execute(delete(model))


def test_slug_is_a_safe_file_name():
    assert slug("Sphyrna lewini") == "sphyrna-lewini"
    assert slug("Carcharodon carcharias (Linnaeus, 1758)") == "carcharodon-carcharias-linnaeus-1758"


def test_export_writes_api_shaped_files(tmp_path):
    with SessionLocal() as session, session.begin():
        _clear(session)
    load(
        {"dataset_id": "export-test", "title": "Export test"},
        None,
        [
            {
                "occurrence_id": "e1",
                "decimal_latitude": -30.123456789,
                "decimal_longitude": 153.987654321,
                "scientific_name": "Sphyrna lewini",
            }
        ],
    )
    with SessionLocal() as session:
        manifest = export(session, tmp_path)

    studies = json.loads((tmp_path / "studies.json").read_text())
    assert [s["dataset_id"] for s in studies] == ["export-test"]
    study_id = studies[0]["id"]
    occurrences = json.loads((tmp_path / f"occurrences/study-{study_id}.geojson").read_text())
    assert occurrences["total"] == 1
    assert occurrences["features"][0]["geometry"]["coordinates"] == [153.98765, -30.12346]
    species = json.loads((tmp_path / "species/sphyrna-lewini.json").read_text())
    assert species["record_count"] == 1
    assert json.loads((tmp_path / "tracks.geojson").read_text())["features"] == []
    assert manifest["files"]["studies.json"] == (tmp_path / "studies.json").stat().st_size
    assert manifest["first_load_gzip_bytes"] < manifest["first_load_budget_bytes"]


def test_export_replaces_stale_files(tmp_path):
    stale = tmp_path / "occurrences" / "study-999.geojson"
    stale.parent.mkdir()
    stale.write_text("{}")
    with SessionLocal() as session:
        export(session, tmp_path)
    assert not stale.exists()
