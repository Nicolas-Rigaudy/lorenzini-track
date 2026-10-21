"""Gateway decoding, deduplication and malformed-message handling (item_002 AC2, AC4), and
track reconstruction (AC3), run on simulator output without a database."""

import json
import logging
from datetime import UTC, datetime, timedelta

import pytest

from app.gateway import decode
from app.gateway.gateway import Gateway
from app.gateway.messages import SatelliteFix
from app.processing.tracks import ProcessingParams, reconstruct
from app.simulator import fleet, formats
from app.simulator.geo import haversine_km

T0 = datetime(2025, 11, 1, tzinfo=UTC)
HEADER = "program,platform_id,satellite,loc_date,loc_class,latitude,longitude,nb_messages,raw_data,simulated\n"
GOOD = "LT-SIM,990001,N15,2025-11-02T03:04:05Z,2,-30.25000,153.30000,3,010D54011171,true\n"


@pytest.fixture(scope="module")
def run():
    return fleet.run(fleet.FleetConfig(seed=9, sharks=3, days=40))


@pytest.fixture(scope="module")
def files(run):
    return formats.render(run)


def loaded(files) -> Gateway:
    gateway = Gateway()
    for name, text in files.items():
        if name.startswith("argos/"):
            gateway.ingest_argos_delivery(name, text)
    gateway.ingest_mqtt_log("mqtt/publishes.jsonl", files["mqtt/publishes.jsonl"])
    return gateway


def test_every_unique_simulated_record_is_stored_once(run, files):
    gateway = loaded(files)
    assert gateway.stats["malformed"] == 0
    assert len(gateway.fixes) == len(run.argos_locations)
    assert len(gateway.detections) == len(run.detections)
    assert gateway.stats["fix_duplicate"] > 0 or gateway.stats["detection_duplicate"] > 0
    assert all(r.simulated for r in [*gateway.fixes.values(), *gateway.detections.values()])


def test_fixes_decode_to_the_simulated_values(run, files):
    gateway = loaded(files)
    for loc in run.argos_locations[:50]:
        fix = gateway.fixes[(loc.platform_id, loc.loc_date)]
        assert fix.loc_class == loc.loc_class
        assert fix.transmissions_total == loc.transmissions_total
        assert (fix.latitude is None) == (loc.latitude is None)
        if loc.latitude is not None:
            assert fix.latitude == pytest.approx(loc.latitude, abs=1e-5)


def test_redelivered_rows_are_stored_once():
    gateway = Gateway()
    gateway.ingest_argos_delivery("LT-SIM_20251102T0600Z.csv", HEADER + GOOD)
    gateway.ingest_argos_delivery("LT-SIM_20251103T0600Z.csv", HEADER + GOOD)
    assert len(gateway.fixes) == 1
    assert gateway.stats["fix_duplicate"] == 1
    # The first delivery wins, so received_at is when the fix first arrived.
    assert next(iter(gateway.fixes.values())).received_at == datetime(2025, 11, 2, 6, tzinfo=UTC)


def test_malformed_messages_are_logged_and_skipped(caplog):
    bad_rows = [
        "LT-SIM,990001,N15,not-a-date,2,-30.25,153.30,3,010D54011171,true\n",
        "LT-SIM,990001,N15,2025-11-02T03:04:05Z,9,-30.25,153.30,3,010D54011171,true\n",
        "LT-SIM,990001,N15,2025-11-02T03:04:05Z,2,-95.0,153.30,3,010D54011171,true\n",
        "LT-SIM,990001,N15,2025-11-02T03:04:05Z,2,-30.25,153.30,3,ZZ,true\n",
        "LT-SIM,990001,N15,2025-11-02T03:04:05Z,2,-30.25,153.30,3,02000000000A,true\n",
        "LT-SIM,abc,N15,2025-11-02T03:04:05Z,2,-30.25,153.30,3,010D54011171,true\n",
    ]
    gateway = Gateway()
    with caplog.at_level(logging.WARNING):
        gateway.ingest_argos_delivery(
            "LT-SIM_20251102T0600Z.csv", HEADER + "".join(bad_rows) + GOOD
        )
        gateway.ingest_mqtt_log("m", "not json\n{}\n")
        gateway.ingest_argos_delivery("oops.csv", HEADER + GOOD)
    assert len(gateway.fixes) == 1
    assert gateway.stats["malformed"] == len(bad_rows) + 2 + 1
    assert "malformed" in caplog.text


def test_class_z_keeps_the_pass_without_a_position():
    row = "LT-SIM,990001,N15,2025-11-02T03:04:05Z,Z,,,1,010D54011171,true\n"
    gateway = Gateway()
    gateway.ingest_argos_delivery("LT-SIM_20251102T0600Z.csv", HEADER + row)
    (fix,) = gateway.fixes.values()
    assert fix.loc_class == "Z" and fix.latitude is None


def test_status_payload_matches_the_simulator_encoder():
    assert decode.decode_spot_status(formats.encode_spot_status(3412, 70_001)) == (3412, 70_001)


# Processing -----------------------------------------------------------------------------------


def fix(hours: float, lat: float, lon: float, loc_class: str = "3", platform: int = 1):
    return SatelliteFix(
        "LT-SIM", platform, "N15", T0 + timedelta(hours=hours), loc_class, lat, lon, 1, 3300, 1,
        T0, True,
    )  # fmt: skip


def test_gaps_stay_gaps_and_classes_are_kept():
    fixes = [fix(0, -30.0, 153.3), fix(5, -30.01, 153.3, "1"), fix(100, -30.02, 153.3, "A")]
    (track,) = reconstruct(fixes)
    assert [len(s) for s in track.segments] == [2, 1]
    assert [p.loc_class for s in track.segments for p in s] == ["3", "1", "A"]


def test_class_z_is_dropped_and_implausible_jumps_are_rejected():
    fixes = [
        fix(0, -30.0, 153.3),
        fix(1, None, None, "Z"),
        fix(2, -30.0, 153.4, "3"),  # about 9.6 km in 2 h from a class 3 fix: too fast
        fix(3, -30.01, 153.3),
    ]
    (track,) = reconstruct(fixes, ProcessingParams(max_speed_kmh=3.0))
    assert len(track.rejected) == 1 and track.rejected[0].longitude == 153.4
    assert [len(s) for s in track.segments] == [2]


def test_argos_error_is_allowed_for_before_judging_speed():
    # 8 km apart in one hour: impossible for two class 3 fixes, plausible with two class B ones.
    near, far = (-30.0, 153.3), (-30.0, 153.3 + 8 / 96.4)
    strict = reconstruct([fix(0, *near), fix(1, *far)], ProcessingParams(max_speed_kmh=3.0))
    lenient = reconstruct(
        [fix(0, *near, "B"), fix(1, *far, "B")], ProcessingParams(max_speed_kmh=3.0)
    )
    assert len(strict[0].rejected) == 1
    assert lenient[0].rejected == []


def test_simulated_tracks_reconstruct_with_every_class(run, files):
    gateway = loaded(files)
    tracks = reconstruct(list(gateway.fixes.values()))
    assert len(tracks) >= 1
    points = [p for t in tracks for s in t.segments for p in s]
    assert points and all(p.loc_class != "Z" for p in points)


def test_broker_payloads_decode_like_the_log_lines(files):
    line = files["mqtt/publishes.jsonl"].splitlines()[0]
    publish = json.loads(line)
    received_at = decode.parse_time(publish["published_at"])
    from_log = decode.decode_mqtt_line(line)
    from_broker = decode.decode_mqtt_payload(
        publish["topic"], formats.dumps(publish["payload"]).encode(), received_at
    )
    assert from_broker == from_log


def test_unreadable_broker_payloads_are_skipped():
    gateway = Gateway()
    gateway.ingest_mqtt_message("lorenzini/sim/receivers/R1/status", b"\xff\x00", T0)
    gateway.ingest_mqtt_message("lorenzini/sim/receivers/R1/status", b'{"format": "x"}', T0)
    assert gateway.stats["malformed"] == 2 and not gateway.statuses


def test_each_delivery_is_recorded_with_its_counts():
    gateway = Gateway()
    gateway.ingest_argos_delivery("LT-SIM_20251102T0600Z.csv", HEADER + GOOD + "x,y\n")
    (delivery,) = gateway.deliveries
    assert (delivery.rows_decoded, delivery.rows_malformed) == (1, 1)
    assert delivery.delivered_at == datetime(2025, 11, 2, 6, tzinfo=UTC)
    assert gateway.fix_delivery == {
        (990001, datetime(2025, 11, 2, 3, 4, 5, tzinfo=UTC)): delivery.name
    }


def test_processed_points_keep_the_published_error_of_their_class():
    # Milestone 0.3 exit signal: about 68 % of the processed points of each class lie within
    # the class's 68th-percentile radius of the true position (costa2010 Table 4).
    run = fleet.run(fleet.FleetConfig(seed=7))
    truth = {(loc.platform_id, loc.loc_date): loc for loc in run.argos_locations}
    gateway = loaded(formats.render(run))
    within: dict[str, list[bool]] = {}
    for track in reconstruct(list(gateway.fixes.values())):
        for point in (p for segment in track.segments for p in segment):
            loc = truth[(track.platform_id, point.fixed_at)]
            distance = haversine_km(
                point.latitude, point.longitude, loc.true_latitude, loc.true_longitude
            )
            within.setdefault(point.loc_class, []).append(distance <= point.error_km)
    pooled = [w for values in within.values() for w in values]
    assert 0.62 <= sum(pooled) / len(pooled) <= 0.75
    for values in within.values():
        if len(values) >= 100:
            assert 0.58 <= sum(values) / len(values) <= 0.78
