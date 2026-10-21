"""Process: rebuild the tracks in PostGIS from the stored satellite fixes.

Runs the speed and quality filter and track reconstruction (`app.processing.tracks`), then the
sensitivity rules hook (`app.processing.sensitivity`), and replaces every stored track of the
platforms it processed. Each fix gets its quality outcome in `satellite_fix.qc`. Re-running on
the same fixes gives the same tracks.
"""

from collections import Counter

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.gateway.messages import SatelliteFix
from app.models.telemetry import SatelliteFixRow, TrackPointRow, TrackSegment
from app.pipeline.store import point
from app.processing.sensitivity import TrackRule, apply_rules
from app.processing.tracks import ProcessingParams, reconstruct


def _line(points) -> str | None:
    if len(points) < 2:
        return None
    return "SRID=4326;LINESTRING(" + ", ".join(f"{p.longitude} {p.latitude}" for p in points) + ")"


def process_tracks(
    session: Session,
    params: ProcessingParams | None = None,
    rules: list[TrackRule] | None = None,
) -> Counter:
    rows = session.scalars(select(SatelliteFixRow).order_by(SatelliteFixRow.id)).all()
    by_key = {(r.platform_id, r.fixed_at): r for r in rows}
    deployment_of = {r.platform_id: r.deployment_id for r in rows}
    fixes = [
        SatelliteFix(
            r.program, r.platform_id, r.satellite, r.fixed_at, r.loc_class, r.latitude,
            r.longitude, r.nb_messages, r.battery_mv, r.transmissions_total, r.received_at,
            r.simulated,
        )
        for r in rows
    ]  # fmt: skip
    tracks = reconstruct(fixes, params)

    counts = Counter()
    qc = {key: "no_position" for key, r in by_key.items() if r.latitude is None}
    platforms = sorted({r.platform_id for r in rows})
    if platforms:
        session.execute(delete(TrackSegment).where(TrackSegment.platform_id.in_(platforms)))
    for track in tracks:
        for fix in track.rejected:
            qc[fix.key] = "speed"
        for segment in track.segments:
            for p in segment:
                qc[(track.platform_id, p.fixed_at)] = "accepted"
        track = apply_rules(track, rules)
        for number, segment in enumerate(s for s in track.segments if s):
            fix_rows = [by_key[(track.platform_id, p.fixed_at)] for p in segment]
            row = TrackSegment(
                deployment_id=deployment_of[track.platform_id],
                platform_id=track.platform_id,
                segment_no=number,
                started_at=segment[0].fixed_at,
                ended_at=segment[-1].fixed_at,
                point_count=len(segment),
                geom=_line(segment),
                simulated=all(f.simulated for f in fix_rows),
            )
            session.add(row)
            session.flush()
            session.add_all(
                TrackPointRow(
                    segment_id=row.id,
                    fix_id=fix_row.id,
                    fixed_at=p.fixed_at,
                    loc_class=p.loc_class,
                    error_km=p.error_km,
                    latitude=p.latitude,
                    longitude=p.longitude,
                    geom=point(p.longitude, p.latitude),
                    simulated=fix_row.simulated,
                )
                for p, fix_row in zip(segment, fix_rows, strict=True)
            )
            counts["segments"] += 1
            counts["points"] += len(segment)
        counts["tracks"] += 1
    for outcome in ("accepted", "speed", "no_position"):
        ids = [by_key[key].id for key, value in qc.items() if value == outcome]
        if ids:
            session.execute(
                update(SatelliteFixRow).where(SatelliteFixRow.id.in_(ids)).values(qc=outcome)
            )
        counts[f"fixes_{outcome}"] = len(ids)
    return counts
