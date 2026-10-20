"""Fleet runs: determinism (AC1), class error and shares in the output (AC2), battery
exhaustion (AC4), and the guarantees item_002 relies on (flags, caps, duty cycle, duplicates)."""

import csv
import dataclasses
import io
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import datetime

import pytest

from app.simulator import argos, fleet, formats, geo
from app.simulator.__main__ import main

SMALL = fleet.FleetConfig(seed=7, sharks=3, days=60)


def with_tags(config: fleet.FleetConfig, **changes) -> fleet.FleetConfig:
    return dataclasses.replace(
        config, satellite_tag=dataclasses.replace(config.satellite_tag, **changes)
    )


def argos_rows(files: dict[str, str]) -> list[dict[str, str]]:
    rows = []
    for path, text in files.items():
        if path.startswith("argos/"):
            rows.extend(csv.DictReader(io.StringIO(text)))
    return rows


def jsonl(files: dict[str, str], path: str) -> list[dict]:
    return [json.loads(line) for line in files[path].splitlines()]


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value)


@pytest.fixture(scope="module")
def default_run() -> fleet.FleetRun:
    return fleet.run(fleet.FleetConfig())


@pytest.fixture(scope="module")
def default_files(default_run) -> dict[str, str]:
    return formats.render(default_run)


# AC1 -----------------------------------------------------------------------------------------


def test_same_seed_writes_byte_identical_files(tmp_path):
    for name in ("a", "b"):
        main(["--seed", "11", "--sharks", "3", "--days", "45", "--out", str(tmp_path / name)])
    a = {
        p.relative_to(tmp_path / "a"): p.read_bytes()
        for p in (tmp_path / "a").rglob("*")
        if p.is_file()
    }
    b = {
        p.relative_to(tmp_path / "b"): p.read_bytes()
        for p in (tmp_path / "b").rglob("*")
        if p.is_file()
    }
    assert a.keys() == b.keys()
    assert all(a[k] == b[k] for k in a)
    assert any(str(k).startswith("argos/") for k in a)


def test_another_seed_changes_the_output():
    other = dataclasses.replace(SMALL, seed=8)
    assert formats.render(fleet.run(SMALL)) != formats.render(fleet.run(other))


def test_adding_a_shark_leaves_the_others_unchanged():
    small, bigger = fleet.run(SMALL), fleet.run(dataclasses.replace(SMALL, sharks=4))
    for shark_id, track in small.tracks.items():
        assert bigger.tracks[shark_id] == track


def test_manifest_lists_every_file_with_its_hash(tmp_path):
    written = formats.write(fleet.run(SMALL), tmp_path / "out")
    record = json.loads((tmp_path / "out" / "manifest.json").read_text())
    listed = {f["path"] for f in record["files"]}
    assert listed == {str(p.relative_to(tmp_path / "out")) for p in written} - {"manifest.json"}
    assert record["seed"] == 7 and record["simulated"] is True


def test_write_refuses_a_non_empty_directory(tmp_path):
    (tmp_path / "keep.txt").write_text("x")
    with pytest.raises(FileExistsError):
        formats.write(fleet.run(SMALL), tmp_path)


# AC2 -----------------------------------------------------------------------------------------


def test_output_class_shares_and_errors_match_the_sources():
    # A larger fleet so each class has enough fixes; errors are measured from the written files
    # against the written truth, the way a downstream check would.
    config = with_tags(
        dataclasses.replace(fleet.FleetConfig(seed=3), sharks=30), failure_mean_days=10_000.0
    )
    files = formats.render(fleet.run(config))
    truth = {
        (str(t["platform_id"]), t["loc_date"]): t for t in jsonl(files, "truth/argos_fixes.jsonl")
    }
    rows = {(r["platform_id"], r["loc_date"]): r for r in argos_rows(files)}  # drops re-deliveries
    shares = Counter(r["loc_class"] for r in rows.values())
    n = sum(shares.values())
    assert n > 3000
    assert (shares["3"] + shares["2"] + shares["1"]) / n == pytest.approx(0.54, abs=0.03)
    assert (shares["A"] + shares["B"]) / n == pytest.approx(0.35, abs=0.03)
    assert shares["Z"] / n < 0.015
    errors = defaultdict(list)
    for key, row in rows.items():
        if row["loc_class"] == "Z":
            continue
        t = truth[key]
        errors[row["loc_class"]].append(
            geo.haversine_km(
                float(row["latitude"]),
                float(row["longitude"]),
                t["true_latitude"],
                t["true_longitude"],
            )
        )
    for lc, values in errors.items():
        values.sort()
        observed = values[int(0.68 * len(values))]
        low, high = argos.ERROR_P68_RANGE_KM[lc]
        # Looser than tests/test_simulator_argos.py: a few hundred fixes per class here.
        assert low * 0.8 <= observed <= high * 1.2, (lc, observed, len(values))


def test_class_z_has_no_position_and_others_do(default_files):
    rows = argos_rows(default_files)
    assert rows
    for row in rows:
        positioned = row["latitude"] != "" and row["longitude"] != ""
        assert positioned == (row["loc_class"] != "Z")


# AC4 -----------------------------------------------------------------------------------------


def test_satellite_tag_stops_when_its_battery_is_exhausted():
    config = with_tags(SMALL, battery_transmissions=60, failure_mean_days=10_000.0)
    run = fleet.run(config)
    files = formats.render(run)
    fates = {
        f["tag_id"]: f for f in jsonl(files, "truth/tag_fates.jsonl") if f["tag_kind"] == "argos"
    }
    for shark in run.sharks:
        fate = fates[str(shark.platform_id)]
        assert fate["reason"] == "battery"
        assert fate["messages_sent"] == 60
        mine = [r for r in argos_rows(files) if r["platform_id"] == str(shark.platform_id)]
        assert all(r["loc_date"] <= fate["ended_at"] for r in mine)
        counters = [formats.decode_spot_status(r["raw_data"])["transmissions_total"] for r in mine]
        assert max(counters, default=0) <= 60


def test_acoustic_tag_stops_when_its_battery_is_exhausted():
    config = dataclasses.replace(
        SMALL, acoustic_tag=dataclasses.replace(SMALL.acoustic_tag, battery_pings=1_000)
    )
    run = fleet.run(config)
    reference = fleet.run(SMALL)
    for shark in run.sharks:
        fate = next(f for f in run.fates if f.tag_id == shark.transmitter_id)
        assert fate.reason == "battery" and fate.messages == 1_000
        mine = [d for d in run.detections if d.transmitter_id == shark.transmitter_id]
        assert all(d.detected_at <= fate.ended_at for d in mine)
        unlimited = [d for d in reference.detections if d.transmitter_id == shark.transmitter_id]
        assert mine == [d for d in unlimited if d.detected_at <= fate.ended_at]
    # The cut-off has to matter: some detections in the reference run come after the death.
    deaths = {f.tag_id: f.ended_at for f in run.fates if f.kind == "acoustic"}
    assert any(d.detected_at > deaths[d.transmitter_id] for d in reference.detections)


def test_tags_without_battery_limit_run_to_failure_or_the_end(default_run):
    for fate in default_run.fates:
        assert fate.reason in {"failure", "end_of_run"}


# Tag behaviour and the item_002 contract ------------------------------------------------------


def test_share_of_days_with_a_location_matches_hammerhead_tags():
    # wells2018 Table 1: median 37% of days with a location, interquartile range 25-47%,
    # over 26 scalloped hammerheads.
    run = fleet.run(dataclasses.replace(fleet.FleetConfig(seed=5), sharks=26))
    shares = []
    for shark in run.sharks:
        fate = next(f for f in run.fates if f.tag_id == str(shark.platform_id))
        days = max(1.0, (fate.ended_at - shark.deployed_at).total_seconds() / 86400)
        located = {
            loc.loc_date.date()
            for loc in run.argos_locations
            if loc.platform_id == shark.platform_id and loc.loc_class != "Z"
        }
        shares.append(min(1.0, len(located) / days))
    assert 0.25 <= statistics.median(shares) <= 0.47


def test_daily_transmission_cap_is_respected():
    config = with_tags(SMALL, surfacings_per_day_median=200.0, surfacings_per_day_log_sd=0.0)
    run = fleet.run(config)
    per_day = Counter()
    last = {}
    for loc in run.argos_locations:
        last[(loc.platform_id, loc.loc_date.date())] = loc.transmissions_total
    assert last
    # Between two located days the counter can grow by at most 250 per calendar day elapsed
    # (days without a location are not observed, so the allowance spans the gap).
    for shark in run.sharks:
        days = sorted(d for p, d in last if p == shark.platform_id)
        previous_day, previous_total = shark.deployed_at.date(), 0
        for day in days:
            total = last[(shark.platform_id, day)]
            elapsed = (day - previous_day).days + 1  # the rest of the previous day counts too
            assert total - previous_total <= 250 * elapsed
            per_day[shark.platform_id] += 1
            previous_day, previous_total = day, total
    assert per_day


def test_duty_cycle_limits_transmissions_to_configured_hours():
    run = fleet.run(with_tags(SMALL, transmit_hours_utc=(0, 1, 2, 3)))
    assert run.argos_locations
    assert {loc.loc_date.hour for loc in run.argos_locations} <= {0, 1, 2, 3}


def test_every_record_is_flagged_simulated(default_files):
    for row in argos_rows(default_files):
        assert row["simulated"] == "true"
    for path in default_files:
        if path.endswith(".jsonl"):
            for record in jsonl(default_files, path):
                assert record.get("simulated", record.get("payload", {}).get("simulated")) is True


def test_receiver_messages_are_ordered_and_duplicates_are_exact(default_files):
    publishes = jsonl(default_files, "mqtt/publishes.jsonl")
    seen: dict[tuple[str, int], dict] = {}
    duplicates = 0
    for p in publishes:
        payload = p["payload"]
        key = (payload["receiver_id"], payload["seq"])
        if key in seen:
            duplicates += 1
            assert seen[key] == payload
        seen[key] = payload
        assert p["published_at"] >= payload["sent_at"]
        assert (
            p["topic"]
            == f"lorenzini/sim/receivers/{payload['receiver_id']}/{p['topic'].rsplit('/', 1)[1]}"
        )
        for det in payload.get("detections", []):
            assert det["detected_at"] <= payload["sent_at"]
    assert duplicates > 0
    assert [p["published_at"] for p in publishes] == sorted(p["published_at"] for p in publishes)


def test_outages_delay_uplinks(default_files):
    late = [
        p
        for p in jsonl(default_files, "mqtt/publishes.jsonl")
        if p["payload"]["format"] == "lt-receiver-status/1"
        and parse_time(p["payload"]["sent_at"]) > parse_time(p["payload"]["status_at"])
    ]
    assert late


def test_redelivered_argos_rows_are_identical(default_files):
    rows = argos_rows(default_files)
    by_key = defaultdict(list)
    for row in rows:
        by_key[(row["platform_id"], row["loc_date"])].append(row)
    repeated = [v for v in by_key.values() if len(v) > 1]
    assert repeated
    assert all(all(r == v[0] for r in v) for v in repeated)


def test_detections_happen_only_within_range(default_run):
    curve = default_run.config.receiver.detection
    assert default_run.detections
    assert max(d.distance_m for d in default_run.detections) <= curve.max_range_m
    median = statistics.median(d.distance_m for d in default_run.detections)
    # More water lies at long range than short, so the median sits past d50 but inside d05.
    assert median < curve.d05_m


def test_spot_payload_round_trips():
    raw = formats.encode_spot_status(3412, 70_001)
    assert raw == "010D54011171"
    assert formats.decode_spot_status(raw) == {"battery_mv": 3412, "transmissions_total": 70_001}


def test_deployments_list_every_shark_and_receiver(default_run, default_files):
    records = jsonl(default_files, "deployments.jsonl")
    kinds = Counter(r["kind"] for r in records)
    assert kinds == {
        "shark": default_run.config.sharks,
        "receiver": len(default_run.config.receivers),
    }
    for r in records:
        assert geo.at_sea(r["latitude"], r["longitude"], buffer_km=0.0)
        assert not math.isnan(r["latitude"])
