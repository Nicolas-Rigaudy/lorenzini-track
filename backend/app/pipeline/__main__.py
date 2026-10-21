"""Run the simulated fleet from a seed to processed tracks in PostGIS, in one command.

    simulate -> deliver (Argos inbox) and replay (MQTT) -> gateway -> ingest -> process

Run from backend/, with PostGIS and Mosquitto up (`docker compose up -d db mqtt`):

    python -m app.pipeline --seed 42

Files go to ../data/pipeline/seed-<seed>/ (simulator output in sim/, Argos deliveries in
inbox/). Running it again with the same seed reuses them and stores nothing twice.
"""

import argparse
import dataclasses
import logging
from datetime import UTC, datetime
from pathlib import Path

from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.core.db import SessionLocal
from app.gateway.gateway import Gateway
from app.gateway.transport import MqttListener, deliver_argos, replay_mqtt_log
from app.pipeline.process import process_tracks
from app.pipeline.store import store_deployments, store_gateway
from app.simulator import fleet, formats

BACKEND_DIR = Path(__file__).resolve().parents[2]
log = logging.getLogger("app.pipeline")


def migrate() -> None:
    # No ini file: alembic.ini's logging section would silence the pipeline's own loggers.
    config = Config()
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    command.upgrade(config, "head")


def simulate(config: fleet.FleetConfig, out: Path) -> None:
    """Write the run to `out`, or reuse what is there if it is the same run."""
    run = fleet.run(config)
    if out.exists() and any(out.iterdir()):
        manifest = out / "manifest.json"
        existing = manifest.read_text(encoding="utf-8") if manifest.exists() else None
        if existing != formats.manifest(run, formats.render(run)):
            raise FileExistsError(f"{out} holds another simulator run; choose another --work")
        log.info("simulate: reusing %s", out)
        return
    formats.write(run, out)
    log.info("simulate: %d sharks, %d days -> %s", config.sharks, config.days, out)


def run_pipeline(
    config: fleet.FleetConfig, work: Path, mqtt_host: str, mqtt_port: int, timeout: float
) -> dict:
    sim, inbox = work / "sim", work / "inbox"
    simulate(config, sim)

    gateway = Gateway()
    delivered = deliver_argos(sim, inbox)
    with MqttListener(gateway, mqtt_host, mqtt_port) as listener:
        replayed = replay_mqtt_log(sim / "mqtt" / "publishes.jsonl", mqtt_host, mqtt_port)
        listener.wait_for_replay(timeout)
    gateway.ingest_inbox(inbox)
    log.info(
        "gateway: %d new Argos deliveries, %d MQTT messages replayed; %s",
        len(delivered),
        replayed,
        dict(sorted(gateway.stats.items())),
    )

    with SessionLocal() as session, session.begin():
        stored = store_deployments(session, sim / "deployments.jsonl")
        new_rows = store_gateway(session, gateway)
        new_rows["deployments"] = stored
    log.info("ingest: new rows %s", dict(sorted(new_rows.items())))

    with SessionLocal() as session, session.begin():
        processed = process_tracks(session)
    log.info("process: %s", dict(sorted(processed.items())))
    return {"gateway": gateway.stats, "stored": new_rows, "processed": processed}


def main(argv: list[str] | None = None) -> None:
    defaults = fleet.FleetConfig()
    parser = argparse.ArgumentParser(prog="python -m app.pipeline", description=__doc__)
    parser.add_argument("--seed", type=int, default=defaults.seed)
    parser.add_argument("--sharks", type=int, default=defaults.sharks)
    parser.add_argument("--days", type=int, default=defaults.days)
    parser.add_argument(
        "--start",
        type=lambda s: datetime.fromisoformat(s).replace(tzinfo=UTC),
        default=defaults.start,
        help="UTC start date, e.g. 2025-11-01",
    )
    parser.add_argument("--work", type=Path, help="default: ../data/pipeline/seed-<seed>")
    parser.add_argument("--mqtt-host", default=settings.mqtt_host)
    parser.add_argument("--mqtt-port", type=int, default=settings.mqtt_port)
    parser.add_argument("--timeout", type=float, default=300.0, help="seconds for the replay")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    config = dataclasses.replace(
        defaults, seed=args.seed, sharks=args.sharks, days=args.days, start=args.start
    )
    work = args.work or BACKEND_DIR.parent / "data" / "pipeline" / f"seed-{args.seed}"
    migrate()
    run_pipeline(config, work, args.mqtt_host, args.mqtt_port, args.timeout)


if __name__ == "__main__":
    main()
