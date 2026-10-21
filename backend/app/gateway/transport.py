"""The two transport networks of decision 0009, for the simulated fleet.

- Satellite tags: Argos-style batch deliveries. `deliver_argos` drops the simulator's batch files
  into an inbox directory, the way Argos delivers processed locations; the gateway reads the
  inbox (`Gateway.ingest_inbox`).
- Receivers and near-real-time trackers: MQTT. `replay_mqtt_log` publishes the simulator's MQTT
  log to the broker in publish order, duplicates included, and `MqttListener` feeds what the
  broker delivers to the gateway.

Simulated time travels with each message as the MQTT 5 user property `published_at`; a message
without it (a live feed) is timestamped with its arrival time.
"""

import json
import logging
import shutil
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Self

import paho.mqtt.client as mqtt
from paho.mqtt.packettypes import PacketTypes
from paho.mqtt.properties import Properties

from app.gateway.decode import MalformedMessage, parse_time
from app.gateway.gateway import Gateway
from app.simulator.formats import dumps

log = logging.getLogger(__name__)

RECEIVER_TOPICS = "lorenzini/sim/receivers/+/+"
REPLAY_DONE_TOPIC = "lorenzini/sim/control/replay-done"
PUBLISHED_AT = "published_at"


def deliver_argos(simulation_dir: Path, inbox: Path) -> list[Path]:
    """Copy every Argos batch of a simulator run into the inbox; already delivered files stay."""
    inbox.mkdir(parents=True, exist_ok=True)
    delivered = []
    for source in sorted((simulation_dir / "argos").glob("*.csv")):
        target = inbox / source.name
        if target.exists():
            if target.read_bytes() != source.read_bytes():
                raise FileExistsError(f"{target} exists with different content")
            continue
        shutil.copyfile(source, target)
        delivered.append(target)
    return delivered


def _client(client_id: str) -> mqtt.Client:
    return mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, protocol=mqtt.MQTTv5)


def replay_mqtt_log(log_path: Path, host: str, port: int, timeout: float = 120.0) -> int:
    """Publish every record of an `lt-mqtt-log/1` file to the broker; return how many."""
    client = _client("lt-sim-replay")
    client.connect(host, port)
    client.loop_start()
    try:
        sent = []
        for line in log_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            properties = Properties(PacketTypes.PUBLISH)
            properties.UserProperty = (PUBLISHED_AT, record["published_at"])
            sent.append(
                client.publish(
                    record["topic"],
                    dumps(record["payload"]),
                    qos=record["qos"],
                    properties=properties,
                )
            )
        done = client.publish(REPLAY_DONE_TOPIC, dumps({"messages": len(sent)}), qos=1)
        for info in [*sent, done]:
            info.wait_for_publish(timeout)
        return len(sent)
    finally:
        client.loop_stop()
        client.disconnect()


def _published_at(message: mqtt.MQTTMessage) -> datetime:
    properties = getattr(message, "properties", None)
    for key, value in getattr(properties, "UserProperty", None) or []:
        if key == PUBLISHED_AT:
            try:
                return parse_time(value)
            except MalformedMessage:
                log.warning("ignored unreadable %s on %s: %r", PUBLISHED_AT, message.topic, value)
    return datetime.now(UTC)


class MqttListener:
    """Subscribes to the receiver topics and hands every message to the gateway.

    Use as a context manager: the subscription is in place when `__enter__` returns, so a
    replay started inside the block loses nothing.
    """

    def __init__(self, gateway: Gateway, host: str, port: int, client_id: str = "lt-gateway"):
        self.gateway = gateway
        self.host, self.port = host, port
        self.received = 0
        self._expected: int | None = None
        self._lock = threading.Lock()
        self._subscribed = threading.Event()
        self._complete = threading.Event()
        self._client = _client(client_id)
        self._client.on_connect = self._on_connect
        self._client.on_subscribe = self._on_subscribe
        self._client.on_message = self._on_message

    def __enter__(self) -> Self:
        self._client.connect(self.host, self.port)
        self._client.loop_start()
        if not self._subscribed.wait(10):
            self.__exit__(None, None, None)
            raise TimeoutError(f"no subscription on the broker at {self.host}:{self.port}")
        return self

    def __exit__(self, *exc) -> None:
        self._client.loop_stop()
        self._client.disconnect()

    def _on_connect(self, client, userdata, flags, reason_code, properties) -> None:
        if reason_code.is_failure:
            log.error("broker refused the connection: %s", reason_code)
            return
        client.subscribe([(RECEIVER_TOPICS, 1), (REPLAY_DONE_TOPIC, 1)])

    def _on_subscribe(self, client, userdata, mid, reason_codes, properties) -> None:
        if all(not code.is_failure for code in reason_codes):
            self._subscribed.set()

    def _on_message(self, client, userdata, message: mqtt.MQTTMessage) -> None:
        with self._lock:
            if message.topic == REPLAY_DONE_TOPIC:
                try:
                    self._expected = int(json.loads(message.payload)["messages"])
                except (KeyError, TypeError, ValueError):
                    log.warning("ignored unreadable replay-done message: %r", message.payload)
            else:
                self.received += 1
                self.gateway.ingest_mqtt_message(
                    message.topic, message.payload, _published_at(message)
                )
            if self._expected is not None and self.received >= self._expected:
                self._complete.set()

    def wait_for_replay(self, timeout: float = 120.0) -> None:
        """Block until the replay-done count has been received."""
        if not self._complete.wait(timeout):
            raise TimeoutError(
                f"received {self.received} of {self._expected} replayed messages in {timeout} s"
            )
