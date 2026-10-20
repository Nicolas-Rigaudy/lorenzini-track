"""Generate a simulated shark tag fleet from a seed.

Run: python -m app.simulator --seed 42 --out ../data/sim/seed-42
"""

import argparse
import dataclasses
from datetime import UTC, datetime
from pathlib import Path

from app.simulator import fleet, formats


def main(argv: list[str] | None = None) -> None:
    defaults = fleet.FleetConfig()
    parser = argparse.ArgumentParser(prog="python -m app.simulator", description=__doc__)
    parser.add_argument("--seed", type=int, default=defaults.seed)
    parser.add_argument("--out", type=Path, required=True, help="empty or new directory")
    parser.add_argument("--sharks", type=int, default=defaults.sharks)
    parser.add_argument("--days", type=int, default=defaults.days)
    parser.add_argument(
        "--start",
        type=lambda s: datetime.fromisoformat(s).replace(tzinfo=UTC),
        default=defaults.start,
        help="UTC start date, e.g. 2025-11-01",
    )
    args = parser.parse_args(argv)
    config = dataclasses.replace(
        defaults, seed=args.seed, sharks=args.sharks, days=args.days, start=args.start
    )
    run = fleet.run(config)
    formats.write(run, args.out)
    print(
        f"seed {config.seed}: {len(run.sharks)} sharks, {len(run.argos_locations)} Argos "
        f"locations in {len(run.argos_deliveries)} deliveries, {len(run.detections)} acoustic "
        f"detections, {len(run.publishes)} MQTT publishes -> {args.out}"
    )


if __name__ == "__main__":
    main()
