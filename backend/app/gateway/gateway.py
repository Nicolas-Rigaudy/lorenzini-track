"""The gateway: reads both transport networks, decodes, deduplicates and timestamps.

Satellite deliveries are timestamped with the delivery time in the file name, receiver
messages with their publish time. Duplicates (the same Argos row redelivered, the same MQTT
message published twice) are stored once; malformed rows are logged and counted, never raised.
"""

import hashlib
import logging
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from app.gateway.decode import (
    MalformedMessage,
    decode_argos_csv,
    decode_mqtt_line,
    decode_mqtt_payload,
)
from app.gateway.messages import AcousticDetection, ReceiverStatus, SatelliteFix

log = logging.getLogger(__name__)

DELIVERY_NAME = re.compile(r"_(\d{8}T\d{4})Z\.csv$")


@dataclass(frozen=True)
class Delivery:
    """One Argos-style batch file and what the gateway made of it."""

    name: str
    delivered_at: datetime
    sha256: str
    rows_decoded: int
    rows_malformed: int
    simulated: bool


@dataclass
class Gateway:
    fixes: dict[tuple, SatelliteFix] = field(default_factory=dict)
    fix_delivery: dict[tuple, str] = field(default_factory=dict)  # first delivery of each fix
    deliveries: list[Delivery] = field(default_factory=list)
    detections: dict[tuple, AcousticDetection] = field(default_factory=dict)
    statuses: dict[tuple, ReceiverStatus] = field(default_factory=dict)
    stats: Counter = field(default_factory=Counter)

    def _store(self, store: dict, record, kind: str) -> None:
        if record.key in store:
            self.stats[f"{kind}_duplicate"] += 1
        else:
            store[record.key] = record
            self.stats[f"{kind}_stored"] += 1

    def _reject(self, source: str, exc: MalformedMessage) -> None:
        self.stats["malformed"] += 1
        log.warning("skipped malformed message from %s: %s", source, exc)

    def ingest_argos_delivery(self, name: str, text: str) -> None:
        match = DELIVERY_NAME.search(name)
        if not match:
            self._reject(name, MalformedMessage("delivery time missing from the file name"))
            return
        received_at = datetime.strptime(match[1], "%Y%m%dT%H%M").replace(tzinfo=UTC)
        decoded = malformed = 0
        simulated = True
        for item in decode_argos_csv(text, received_at):
            if isinstance(item, MalformedMessage):
                self._reject(name, item)
                malformed += 1
            else:
                decoded += 1
                simulated = simulated and item.simulated
                self.fix_delivery.setdefault(item.key, name)
                self._store(self.fixes, item, "fix")
        sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()
        self.deliveries.append(Delivery(name, received_at, sha256, decoded, malformed, simulated))

    def ingest_mqtt_log(self, source: str, text: str) -> None:
        for number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                records = decode_mqtt_line(line)
            except MalformedMessage as exc:
                self._reject(f"{source}:{number}", exc)
                continue
            self._store_receiver_records(records)

    def ingest_mqtt_message(self, topic: str, payload: bytes, received_at: datetime) -> None:
        """One message as delivered by the broker; `received_at` is its publish time."""
        try:
            records = decode_mqtt_payload(topic, payload, received_at)
        except MalformedMessage as exc:
            self._reject(topic, exc)
            return
        self._store_receiver_records(records)

    def _store_receiver_records(self, records) -> None:
        for record in records:
            if isinstance(record, AcousticDetection):
                self._store(self.detections, record, "detection")
            else:
                self._store(self.statuses, record, "status")

    def ingest_inbox(self, inbox: Path) -> None:
        """Read every Argos-style delivery in an inbox directory, oldest first."""
        for path in sorted(inbox.glob("*.csv")):
            self.ingest_argos_delivery(path.name, path.read_text(encoding="utf-8"))

    def ingest_directory(self, directory: Path) -> None:
        """Read a simulator output directory in delivery order, without the broker."""
        self.ingest_inbox(directory / "argos")
        mqtt_log = directory / "mqtt" / "publishes.jsonl"
        if mqtt_log.exists():
            self.ingest_mqtt_log(str(mqtt_log), mqtt_log.read_text(encoding="utf-8"))
