"""Integration: seed -> Argos inbox and MQTT broker -> gateway -> PostGIS -> tracks (item_002).

Needs the disposable PostGIS and Mosquitto that backend/scripts/test.sh starts.
"""

import dataclasses
import json
import logging
from datetime import timedelta
from itertools import pairwise

import pytest
from sqlalchemy import func, select, text

from app.core.config import settings
from app.core.db import SessionLocal
from app.gateway.gateway import Gateway
from app.gateway.transport import MqttListener, replay_mqtt_log
from app.models.telemetry import (
    AcousticDetectionRow,
    ArgosDelivery,
    Deployment,
    ReceiverStatusRow,
    SatelliteFixRow,
    TrackPointRow,
    TrackSegment,
)
from app.pipeline.__main__ import run_pipeline
from app.pipeline.process import process_tracks
from app.processing.tracks import ProcessingParams
from app.simulator import fleet

TABLES = [
    TrackPointRow,
    TrackSegment,
    SatelliteFixRow,
    AcousticDetectionRow,
    ReceiverStatusRow,
    ArgosDelivery,
    Deployment,
]
CONFIG = dataclasses.replace(fleet.FleetConfig(), seed=9, sharks=3, days=60)
BAD_DELIVERY = (
    "program,platform_id,satellite,loc_date,loc_class,latitude,longitude,nb_messages,raw_data,"
    "simulated\nLT-SIM,990001,N15,not-a-date,2,-30.25,153.30,3,010D54011171,true\n"
)


def run(work):
    return run_pipeline(CONFIG, work, settings.mqtt_host, settings.mqtt_port, timeout=60)


def count(session, model, *where) -> int:
    return session.scalar(select(func.count()).select_from(model).where(*where))


@pytest.fixture(scope="module")
def pipeline(tmp_path_factory):
    with SessionLocal() as session, session.begin():
        names = ", ".join(model.__tablename__ for model in TABLES)
        session.execute(text(f"TRUNCATE {names} RESTART IDENTITY CASCADE"))
    work = tmp_path_factory.mktemp("pipeline")
    # A malformed delivery sits in the inbox before the run: it must be logged and skipped.
    (work / "inbox").mkdir()
    (work / "inbox" / "LT-SIM_20200101T0000Z.csv").write_text(BAD_DELIVERY)
    first = run(work)
    second = run(work)
    return work, first, second


def test_one_command_takes_a_seed_to_tracks_in_postgis(pipeline):
    _, first, _ = pipeline
    simulated = fleet.run(CONFIG)
    with SessionLocal() as session:
        assert count(session, SatelliteFixRow) == len(simulated.argos_locations)
        assert count(session, AcousticDetectionRow) == len(simulated.detections)
        assert count(session, TrackSegment) == first["processed"]["segments"] > 0
        assert count(session, TrackPointRow) == count(
            session, SatelliteFixRow, SatelliteFixRow.qc == "accepted"
        )
        unlinked = count(session, SatelliteFixRow, SatelliteFixRow.deployment_id.is_(None))
        assert unlinked == 0


def test_duplicates_are_stored_once_and_a_rerun_adds_nothing(pipeline):
    _, first, second = pipeline
    assert first["gateway"]["fix_duplicate"] + first["gateway"]["status_duplicate"] > 0
    assert first["stored"]["fixes"] == first["gateway"]["fix_stored"]
    assert first["stored"]["statuses"] == first["gateway"]["status_stored"]
    assert sum(second["stored"].values()) == 0
    assert second["processed"] == first["processed"]


def test_malformed_deliveries_are_logged_and_skipped(pipeline):
    _, first, _ = pipeline
    assert first["gateway"]["malformed"] == 1
    with SessionLocal() as session:
        bad = session.scalar(select(ArgosDelivery).where(ArgosDelivery.name.like("%2020%")))
        assert (bad.rows_decoded, bad.rows_malformed) == (0, 1)


def test_malformed_broker_messages_are_logged_and_skipped(tmp_path, caplog):
    good = {
        "detections_total": 0, "format": "lt-receiver-status/1", "receiver_id": "R1",
        "sent_at": "2025-11-02T00:00:00Z", "seq": 1, "simulated": True,
        "status_at": "2025-11-02T00:00:00Z",
    }  # fmt: skip
    topic = "lorenzini/sim/receivers/R1/status"
    records = [
        {"published_at": "2025-11-02T00:00:01Z", "qos": 1, "topic": topic, "payload": good},
        {"published_at": "2025-11-02T00:00:02Z", "qos": 1, "topic": topic, "payload": [1]},
        {"published_at": "2025-11-02T00:00:03Z", "qos": 1, "topic": topic, "payload": good},
    ]
    log_path = tmp_path / "publishes.jsonl"
    log_path.write_text("".join(json.dumps(r) + "\n" for r in records))
    gateway = Gateway()
    listener = MqttListener(gateway, settings.mqtt_host, settings.mqtt_port, "lt-test")
    with caplog.at_level(logging.WARNING), listener:
        replay_mqtt_log(log_path, settings.mqtt_host, settings.mqtt_port)
        listener.wait_for_replay(30)
    assert listener.received == 3
    assert gateway.stats["malformed"] == 1 and "malformed" in caplog.text
    assert gateway.stats["status_duplicate"] == 1
    (status,) = gateway.statuses.values()
    # Timestamped with the simulated publish time carried by the message, not the wall clock.
    assert status.received_at.isoformat() == "2025-11-02T00:00:01+00:00"


def test_tracks_keep_gaps_as_gaps_and_the_class_of_each_fix(pipeline):
    gap = timedelta(hours=ProcessingParams().gap_hours)
    with SessionLocal() as session:
        points = session.execute(
            select(TrackPointRow, SatelliteFixRow.loc_class, TrackSegment)
            .join(SatelliteFixRow, TrackPointRow.fix_id == SatelliteFixRow.id)
            .join(TrackSegment, TrackPointRow.segment_id == TrackSegment.id)
            .order_by(TrackSegment.platform_id, TrackPointRow.fixed_at)
        ).all()
        assert points and all(p.loc_class == fix_class for p, fix_class, _ in points)
        assert {p.loc_class for p, _, _ in points} > {"B"}
        assert count(session, TrackPointRow, TrackPointRow.loc_class == "Z") == 0
        gaps = 0
        for (a, _, sa), (b, _, sb) in pairwise(points):
            if sa.platform_id != sb.platform_id:
                continue
            if sa.id == sb.id:
                assert b.fixed_at - a.fixed_at <= gap
            else:
                assert b.fixed_at - a.fixed_at > gap and sb.segment_no == sa.segment_no + 1
                gaps += 1
        assert gaps > 0
        lines = session.scalar(
            select(func.count())
            .select_from(TrackSegment)
            .where(TrackSegment.point_count > 1, func.ST_NPoints(TrackSegment.geom) > 1)
        )
        assert lines == count(session, TrackSegment, TrackSegment.point_count > 1)


def test_every_stored_record_is_flagged_simulated(pipeline):
    with SessionLocal() as session:
        for model in TABLES:
            assert count(session, model) > 0, model.__tablename__
            assert count(session, model, model.simulated.is_(False)) == 0, model.__tablename__


def test_sensitivity_rules_run_before_tracks_are_stored(pipeline):
    def coarsen(track):
        segments = [
            [dataclasses.replace(p, latitude=round(p.latitude, 1)) for p in segment]
            for segment in track.segments
        ]
        return dataclasses.replace(track, segments=segments)

    try:
        with SessionLocal() as session, session.begin():
            process_tracks(session, rules=[coarsen])
        with SessionLocal() as session:
            latitudes = session.scalars(select(TrackPointRow.latitude)).all()
            assert latitudes and all(lat == round(lat, 1) for lat in latitudes)
    finally:
        with SessionLocal() as session, session.begin():
            process_tracks(session)
