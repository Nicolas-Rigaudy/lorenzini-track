"""Ingest: write deployments and what the gateway decoded into the telemetry tables.

Every insert is `ON CONFLICT DO NOTHING` on the gateway's dedup keys, so a message already
stored (redelivered, or ingested by an earlier run) is stored once and keeps the time it first
arrived.
"""

import json
from collections import Counter
from pathlib import Path

from sqlalchemy import update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from app.gateway.decode import parse_time
from app.gateway.gateway import Gateway
from app.models.telemetry import (
    AcousticDetectionRow,
    ArgosDelivery,
    Deployment,
    ReceiverStatusRow,
    SatelliteFixRow,
)

DEPLOYMENT_FORMAT = "lt-deployment/1"
CHUNK = 2000


def point(longitude: float, latitude: float) -> str:
    return f"SRID=4326;POINT({longitude} {latitude})"


def _insert(session: Session, model, rows: list[dict]) -> int:
    """Insert rows, skipping those that hit a unique constraint; return how many were new."""
    inserted = 0
    for start in range(0, len(rows), CHUNK):
        chunk = rows[start : start + CHUNK]
        result = session.execute(
            insert(model).values(chunk).on_conflict_do_nothing().returning(model.id)
        )
        inserted += len(result.all())
    return inserted


def deployment_rows(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("format") != DEPLOYMENT_FORMAT:
            raise ValueError(f"not an {DEPLOYMENT_FORMAT} record: {line[:80]}")
        row = {
            "kind": record["kind"],
            "deployed_at": parse_time(record["deployed_at"]),
            "latitude": record["latitude"],
            "longitude": record["longitude"],
            "geom": point(record["longitude"], record["latitude"]),
            "simulated": record["simulated"] is True,
            "scientific_name": None,
            "vernacular_name": None,
            "receiver_line": None,
            "argos_program": None,
            "platform_id": None,
            "transmitter_id": None,
        }
        if record["kind"] == "shark":
            row["deployment_ref"] = record["shark_id"]
            row["scientific_name"] = record["scientific_name"]
            row["vernacular_name"] = record["vernacular_name"]
            for tag in record["tags"]:
                if tag["kind"] == "argos":
                    row["argos_program"] = tag["program"]
                    row["platform_id"] = tag["platform_id"]
                elif tag["kind"] == "acoustic":
                    row["transmitter_id"] = tag["transmitter_id"]
        else:
            row["deployment_ref"] = record["receiver_id"]
            row["receiver_line"] = record["line"]
        rows.append(row)
    return rows


def store_deployments(session: Session, path: Path) -> int:
    return _insert(session, Deployment, deployment_rows(path.read_text(encoding="utf-8")))


def _fix_row(fix, delivery_name: str | None) -> dict:
    has_position = fix.latitude is not None
    return {
        "program": fix.program,
        "platform_id": fix.platform_id,
        "satellite": fix.satellite,
        "fixed_at": fix.fixed_at,
        "loc_class": fix.loc_class,
        "latitude": fix.latitude,
        "longitude": fix.longitude,
        "geom": point(fix.longitude, fix.latitude) if has_position else None,
        "nb_messages": fix.nb_messages,
        "battery_mv": fix.battery_mv,
        "transmissions_total": fix.transmissions_total,
        "received_at": fix.received_at,
        "delivery_name": delivery_name,
        "simulated": fix.simulated,
    }


def _by_time(records, when: str) -> list:
    # Insert in time order so ids follow the data, whatever order the networks delivered it in.
    return sorted(records, key=lambda r: (getattr(r, when), r.key))


def store_gateway(session: Session, gateway: Gateway) -> Counter:
    """Store the gateway's records and link them to their deployments; return new-row counts."""
    stored = Counter()
    stored["deliveries"] = _insert(
        session,
        ArgosDelivery,
        [
            {
                "name": d.name,
                "delivered_at": d.delivered_at,
                "sha256": d.sha256,
                "rows_decoded": d.rows_decoded,
                "rows_malformed": d.rows_malformed,
                "simulated": d.simulated,
            }
            for d in gateway.deliveries
        ],
    )
    stored["fixes"] = _insert(
        session,
        SatelliteFixRow,
        [
            _fix_row(f, gateway.fix_delivery.get(f.key))
            for f in _by_time(gateway.fixes.values(), "fixed_at")
        ],
    )
    stored["detections"] = _insert(
        session,
        AcousticDetectionRow,
        [
            {
                "receiver_id": d.receiver_id,
                "transmitter_id": d.transmitter_id,
                "detected_at": d.detected_at,
                "received_at": d.received_at,
                "simulated": d.simulated,
            }
            for d in _by_time(gateway.detections.values(), "detected_at")
        ],
    )
    stored["statuses"] = _insert(
        session,
        ReceiverStatusRow,
        [
            {
                "receiver_id": s.receiver_id,
                "status_at": s.status_at,
                "detections_total": s.detections_total,
                "received_at": s.received_at,
                "simulated": s.simulated,
            }
            for s in _by_time(gateway.statuses.values(), "status_at")
        ],
    )
    link_deployments(session)
    return stored


def link_deployments(session: Session) -> None:
    """Point fixes and detections at the shark deployment carrying their tag."""
    session.execute(
        update(SatelliteFixRow)
        .where(
            SatelliteFixRow.deployment_id.is_(None),
            SatelliteFixRow.platform_id == Deployment.platform_id,
        )
        .values(deployment_id=Deployment.id)
    )
    session.execute(
        update(AcousticDetectionRow)
        .where(
            AcousticDetectionRow.deployment_id.is_(None),
            AcousticDetectionRow.transmitter_id == Deployment.transmitter_id,
        )
        .values(deployment_id=Deployment.id)
    )
