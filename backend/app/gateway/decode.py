"""Decode raw Argos CSV rows and receiver MQTT messages into normalized records.

Every decoder raises `MalformedMessage` on input it cannot trust; the gateway logs those and
moves on, so one bad row never stops a delivery.
"""

import csv
import io
import json
from datetime import UTC, datetime

from app.gateway.messages import AcousticDetection, ReceiverStatus, SatelliteFix

ARGOS_CSV_FORMAT = "lt-argos-csv/1"
DETECTIONS_FORMAT = "lt-receiver-detections/1"
STATUS_FORMAT = "lt-receiver-status/1"
LOC_CLASSES = frozenset("3210AB")
PAYLOAD_TYPE_SPOT_STATUS = 0x01


class MalformedMessage(ValueError):
    pass


def parse_time(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise MalformedMessage(f"timestamp is not UTC ISO 8601 with a Z suffix: {value!r}")
    try:
        return datetime.fromisoformat(value).astimezone(UTC)
    except ValueError as exc:
        raise MalformedMessage(f"unreadable timestamp: {value!r}") from exc


def decode_spot_status(raw: str) -> tuple[int, int]:
    """(battery_mv, transmissions_total) from the six-byte hex payload."""
    try:
        data = bytes.fromhex(raw)
    except ValueError as exc:
        raise MalformedMessage(f"payload is not hex: {raw!r}") from exc
    if len(data) != 6 or data[0] != PAYLOAD_TYPE_SPOT_STATUS:
        raise MalformedMessage(f"not a status payload: {raw!r}")
    return int.from_bytes(data[1:3], "big"), int.from_bytes(data[3:6], "big")


def _coordinate(text: str, low: float, high: float) -> float:
    value = float(text)
    if not low <= value <= high:
        raise ValueError(text)
    return value


def decode_argos_row(row: dict[str, str], received_at: datetime) -> SatelliteFix:
    try:
        loc_class = row["loc_class"]
        if loc_class != "Z" and loc_class not in LOC_CLASSES:
            raise MalformedMessage(f"unknown location class: {loc_class!r}")
        if loc_class == "Z":
            latitude = longitude = None
        else:
            latitude = _coordinate(row["latitude"], -90.0, 90.0)
            longitude = _coordinate(row["longitude"], -180.0, 180.0)
        battery_mv, transmissions_total = decode_spot_status(row["raw_data"])
        return SatelliteFix(
            program=row["program"],
            platform_id=int(row["platform_id"]),
            satellite=row["satellite"],
            fixed_at=parse_time(row["loc_date"]),
            loc_class=loc_class,
            latitude=latitude,
            longitude=longitude,
            nb_messages=int(row["nb_messages"]),
            battery_mv=battery_mv,
            transmissions_total=transmissions_total,
            received_at=received_at,
            simulated=row["simulated"] == "true",
        )
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, MalformedMessage):
            raise
        raise MalformedMessage(f"unreadable Argos row {row!r}: {exc!r}") from exc


def decode_argos_csv(text: str, received_at: datetime):
    """Yield a SatelliteFix or a MalformedMessage for every row of one delivery."""
    for row in csv.DictReader(io.StringIO(text)):
        try:
            yield decode_argos_row(row, received_at)
        except MalformedMessage as exc:
            yield exc


def decode_receiver_message(topic: str, payload: object, received_at: datetime):
    """Decode one receiver message (topic and parsed JSON payload) into detections or a status."""
    try:
        receiver_id = payload["receiver_id"]
        simulated = payload["simulated"] is True
        topic_kind = topic.rsplit("/", 1)[-1]
        if payload["format"] == DETECTIONS_FORMAT and topic_kind == "detections":
            return [
                AcousticDetection(
                    receiver_id,
                    str(d["transmitter_id"]),
                    parse_time(d["detected_at"]),
                    received_at,
                    simulated,
                )
                for d in payload["detections"]
            ]
        if payload["format"] == STATUS_FORMAT and topic_kind == "status":
            return [
                ReceiverStatus(
                    receiver_id,
                    parse_time(payload["status_at"]),
                    int(payload["detections_total"]),
                    received_at,
                    simulated,
                )
            ]
    except MalformedMessage:
        raise
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise MalformedMessage(f"unreadable receiver message: {exc!r}") from exc
    raise MalformedMessage(f"unknown receiver message format: {payload.get('format')!r}")


def decode_mqtt_payload(topic: str, payload: bytes, received_at: datetime):
    """Decode a message as it arrives from the broker: raw payload bytes, JSON inside."""
    try:
        message = json.loads(payload)
    except (UnicodeDecodeError, ValueError) as exc:
        raise MalformedMessage(f"payload is not JSON: {exc!r}") from exc
    return decode_receiver_message(topic, message, received_at)


def decode_mqtt_line(line: str):
    """Decode one line of the MQTT log into AcousticDetection or ReceiverStatus records."""
    try:
        publish = json.loads(line)
        topic, payload, published_at = publish["topic"], publish["payload"], publish["published_at"]
    except (KeyError, TypeError, ValueError) as exc:
        raise MalformedMessage(f"unreadable MQTT log line: {exc!r}") from exc
    return decode_receiver_message(topic, payload, parse_time(published_at))
