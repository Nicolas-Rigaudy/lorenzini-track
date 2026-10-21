"""Export the database to static files for the hosted demo (item_005).

Run from backend/, with the occurrence and track tables filled:

    python -m app.export --out ../frontend/public/data

Writes what the API serves, as files the frontend reads in static mode:

    studies.json                      GET /studies
    species.json                      GET /species
    species/<slug>.json               GET /species/<name>
    occurrences/study-<id>.geojson    GET /occurrences?study_id=<id>
    tracks.geojson                    processed tracks (after the sensitivity rules)
    manifest.json                     file sizes and the size budget

Tracks are read from `track_segment` and `track_point`, which hold the output of the
sensitivity rules; raw fixes are never exported.
"""

import argparse
import gzip
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.routes.occurrences import list_occurrences
from app.api.routes.species import get_species, list_species
from app.api.routes.studies import list_studies
from app.core.db import SessionLocal
from app.models.study import Study
from app.models.telemetry import Deployment, TrackPointRow, TrackSegment

COORD_DECIMALS = 5
# Gzipped bytes the first screen may cost (studies.json + species.json); GitHub Pages gzips.
FIRST_LOAD_BUDGET = 150_000


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _round(value):
    if isinstance(value, float):
        return round(value, COORD_DECIMALS)
    if isinstance(value, list):
        return [_round(v) for v in value]
    return value


def write_json(path: Path, data) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")
    return path.stat().st_size


def occurrences(session: Session, study_id: int) -> dict:
    data = list_occurrences(study_id=study_id, scientific_name=None, db=session)
    for feature in data["features"]:
        feature["geometry"]["coordinates"] = _round(feature["geometry"]["coordinates"])
    return data


def _iso(value: datetime) -> str:
    return value.isoformat()


def tracks(session: Session) -> dict:
    refs = {d.id: d for d in session.scalars(select(Deployment).where(Deployment.kind == "shark"))}
    features = []
    segments = session.scalars(
        select(TrackSegment).order_by(TrackSegment.deployment_id, TrackSegment.segment_no)
    ).all()
    for segment in segments:
        deployment = refs.get(segment.deployment_id)
        base = {
            "shark_id": deployment.deployment_ref if deployment else None,
            "scientific_name": deployment.scientific_name if deployment else None,
            "segment_no": segment.segment_no,
            "simulated": segment.simulated,
        }
        points = session.scalars(
            select(TrackPointRow)
            .where(TrackPointRow.segment_id == segment.id)
            .order_by(TrackPointRow.fixed_at)
        ).all()
        if len(points) > 1:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [_round([p.longitude, p.latitude]) for p in points],
                    },
                    "properties": {
                        **base,
                        "kind": "segment",
                        "started_at": _iso(segment.started_at),
                        "ended_at": _iso(segment.ended_at),
                        "point_count": segment.point_count,
                    },
                }
            )
        for p in points:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": _round([p.longitude, p.latitude]),
                    },
                    "properties": {
                        **base,
                        "kind": "point",
                        "fixed_at": _iso(p.fixed_at),
                        "loc_class": p.loc_class,
                        "error_km": p.error_km,
                    },
                }
            )
    return {"type": "FeatureCollection", "features": features}


def export(session: Session, out: Path) -> dict:
    # Clear only what this command writes, so a stale file never ships.
    for name in ("studies.json", "species.json", "tracks.geojson", "manifest.json"):
        (out / name).unlink(missing_ok=True)
    for name in ("species", "occurrences"):
        shutil.rmtree(out / name, ignore_errors=True)

    sizes: dict[str, int] = {}
    sizes["studies.json"] = write_json(out / "studies.json", list_studies(db=session))
    species = list_species(db=session)
    sizes["species.json"] = write_json(out / "species.json", species)
    for item in species:
        name = item["scientific_name"]
        path = f"species/{slug(name)}.json"
        sizes[path] = write_json(out / path, get_species(name, db=session))
    for study_id in session.scalars(select(Study.id).order_by(Study.id)):
        path = f"occurrences/study-{study_id}.geojson"
        sizes[path] = write_json(out / path, occurrences(session, study_id))
    sizes["tracks.geojson"] = write_json(out / "tracks.geojson", tracks(session))

    first_load = sum(
        len(gzip.compress((out / name).read_bytes())) for name in ("studies.json", "species.json")
    )
    manifest = {
        "first_load_budget_bytes": FIRST_LOAD_BUDGET,
        "first_load_gzip_bytes": first_load,
        "total_bytes": sum(sizes.values()),
        "files": dict(sorted(sizes.items())),
    }
    write_json(out / "manifest.json", manifest)
    return manifest


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.export", description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    with SessionLocal() as session:
        manifest = export(session, args.out)
    print(f"exported {len(manifest['files'])} files, {manifest['total_bytes']} bytes -> {args.out}")
    if manifest["first_load_gzip_bytes"] > FIRST_LOAD_BUDGET:
        raise SystemExit(
            f"first-load data is {manifest['first_load_gzip_bytes']} bytes gzipped, "
            f"over the {FIRST_LOAD_BUDGET} budget"
        )


if __name__ == "__main__":
    main()
