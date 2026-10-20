"""Write a fleet run as raw files: the formats item_002's gateway consumes.

The formats are specified in logics/architecture/adr_001_raw_tag_and_receiver_message_formats.md;
change them only together with that document. Output is byte-identical for the same seed and
configuration: keys are sorted, numbers have fixed precision, rows and files have a fixed
order, and nothing depends on the wall clock.
"""

import csv
import dataclasses
import hashlib
import io
import json
from datetime import UTC, datetime
from pathlib import Path

from app.simulator.fleet import SPECIES_SCIENTIFIC, SPECIES_VERNACULAR, ArgosLocation, FleetRun

SIMULATOR_VERSION = "1"
ARGOS_CSV_FORMAT = "lt-argos-csv/1"
DEPLOYMENT_FORMAT = "lt-deployment/1"
MQTT_LOG_FORMAT = "lt-mqtt-log/1"
TRUTH_FORMAT = "lt-truth/1"
PAYLOAD_TYPE_SPOT_STATUS = 0x01

ARGOS_COLUMNS = (
    "program",
    "platform_id",
    "satellite",
    "loc_date",
    "loc_class",
    "latitude",
    "longitude",
    "nb_messages",
    "raw_data",
    "simulated",
)


def iso(when: datetime) -> str:
    return when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def coord(value: float | None) -> float | None:
    """Coordinates in JSON: degrees rounded to 5 decimals (about 1 m)."""
    return None if value is None else round(value, 5)


def csv_coord(value: float | None) -> str:
    """Coordinates in CSV: 5 fixed decimals, empty when there is no position (class Z)."""
    return "" if value is None else f"{value:.5f}"


def dumps(obj: object) -> str:
    """Canonical JSON: sorted keys, no spaces, ASCII. MQTT payloads go on the wire like this."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def encode_spot_status(battery_mv: int, transmissions_total: int) -> str:
    """Six-byte tag payload as upper-case hex: type (1 byte), battery in mV (uint16 big-endian),
    transmissions since deployment (uint24 big-endian)."""
    payload = (
        PAYLOAD_TYPE_SPOT_STATUS.to_bytes(1, "big")
        + battery_mv.to_bytes(2, "big")
        + min(transmissions_total, 0xFFFFFF).to_bytes(3, "big")
    )
    return payload.hex().upper()


def decode_spot_status(raw: str) -> dict[str, int]:
    data = bytes.fromhex(raw)
    if len(data) != 6 or data[0] != PAYLOAD_TYPE_SPOT_STATUS:
        raise ValueError(f"not a SPOT status payload: {raw!r}")
    return {
        "battery_mv": int.from_bytes(data[1:3], "big"),
        "transmissions_total": int.from_bytes(data[3:6], "big"),
    }


def _argos_rows(program: str, locations: list[ArgosLocation]) -> str:
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(ARGOS_COLUMNS)
    for loc in locations:
        writer.writerow(
            (
                program,
                loc.platform_id,
                loc.satellite,
                iso(loc.loc_date),
                loc.loc_class,
                csv_coord(loc.latitude),
                csv_coord(loc.longitude),
                loc.nb_messages,
                encode_spot_status(loc.battery_mv, loc.transmissions_total),
                "true",
            )
        )
    return out.getvalue()


def _jsonl(records: list[dict]) -> str:
    return "".join(dumps(r) + "\n" for r in records)


def _config_record(run: FleetRun) -> dict:
    def plain(value: object) -> object:
        if isinstance(value, datetime):
            return iso(value)
        if isinstance(value, dict):
            return {k: plain(v) for k, v in value.items()}
        if isinstance(value, list | tuple):
            return [plain(v) for v in value]
        return value

    config = dataclasses.asdict(run.config)
    config.pop("receivers")  # listed one per line in deployments.jsonl
    return plain(config)


def render(run: FleetRun) -> dict[str, str]:
    """Every output file as {relative path: text}, without the manifest."""
    cfg = run.config
    files: dict[str, str] = {}

    deployments = [
        {
            "format": DEPLOYMENT_FORMAT,
            "kind": "shark",
            "shark_id": s.shark_id,
            "scientific_name": SPECIES_SCIENTIFIC,
            "vernacular_name": SPECIES_VERNACULAR,
            "deployed_at": iso(s.deployed_at),
            "latitude": coord(s.latitude),
            "longitude": coord(s.longitude),
            "tags": [
                {"kind": "argos", "program": cfg.argos_program, "platform_id": s.platform_id},
                {"kind": "acoustic", "transmitter_id": s.transmitter_id},
            ],
            "simulated": True,
        }
        for s in run.sharks
    ] + [
        {
            "format": DEPLOYMENT_FORMAT,
            "kind": "receiver",
            "receiver_id": rc.receiver_id,
            "line": rc.line,
            "deployed_at": iso(cfg.start),
            "latitude": coord(rc.latitude),
            "longitude": coord(rc.longitude),
            "simulated": True,
        }
        for rc in cfg.receivers
    ]
    files["deployments.jsonl"] = _jsonl(deployments)

    for delivered_at, batch in run.argos_deliveries.items():
        name = f"argos/{cfg.argos_program}_{delivered_at.strftime('%Y%m%dT%H%MZ')}.csv"
        files[name] = _argos_rows(cfg.argos_program, batch)

    files["mqtt/publishes.jsonl"] = _jsonl(
        [
            {
                "format": MQTT_LOG_FORMAT,
                "published_at": iso(p.published_at),
                "qos": 1,
                "topic": p.topic,
                "payload": p.payload,
            }
            for p in run.publishes
        ]
    )

    files["truth/tracks.jsonl"] = _jsonl(
        [
            {
                "format": TRUTH_FORMAT,
                "kind": "position",
                "shark_id": shark_id,
                "time": iso(p.time),
                "latitude": coord(p.latitude),
                "longitude": coord(p.longitude),
                "state": p.state,
                "simulated": True,
            }
            for shark_id, track in run.tracks.items()
            for p in track
        ]
    )
    files["truth/argos_fixes.jsonl"] = _jsonl(
        [
            {
                "format": TRUTH_FORMAT,
                "kind": "argos_fix",
                "platform_id": loc.platform_id,
                "loc_date": iso(loc.loc_date),
                "loc_class": loc.loc_class,
                "true_latitude": coord(loc.true_latitude),
                "true_longitude": coord(loc.true_longitude),
                "error_m": None if loc.error_km is None else round(loc.error_km * 1000),
                "simulated": True,
            }
            for loc in run.argos_locations
        ]
    )
    files["truth/tag_fates.jsonl"] = _jsonl(
        [
            {
                "format": TRUTH_FORMAT,
                "kind": "tag_fate",
                "tag_kind": f.kind,
                "tag_id": f.tag_id,
                "shark_id": f.shark_id,
                "ended_at": iso(f.ended_at),
                "reason": f.reason,
                "messages_sent": f.messages,
                "simulated": True,
            }
            for f in run.fates
        ]
    )
    return dict(sorted(files.items()))


def manifest(run: FleetRun, files: dict[str, str]) -> str:
    record = {
        "simulator_version": SIMULATOR_VERSION,
        "seed": run.config.seed,
        "config": _config_record(run),
        "formats": {
            "argos": ARGOS_CSV_FORMAT,
            "deployments": DEPLOYMENT_FORMAT,
            "mqtt": MQTT_LOG_FORMAT,
            "truth": TRUTH_FORMAT,
        },
        "files": [
            {
                "path": path,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "lines": text.count("\n"),
            }
            for path, text in files.items()
        ],
        "simulated": True,
    }
    return json.dumps(record, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def write(run: FleetRun, out_dir: Path) -> list[Path]:
    """Write the run into `out_dir`, which must not exist yet or be empty."""
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"{out_dir} is not empty")
    files = render(run)
    files["manifest.json"] = manifest(run, files)
    written = []
    for rel, text in files.items():
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))
        written.append(path)
    return written
