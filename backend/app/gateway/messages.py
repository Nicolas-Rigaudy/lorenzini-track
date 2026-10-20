"""Normalized records the gateway produces from raw tag and receiver messages.

Raw formats are specified in logics/architecture/adr_001_raw_tag_and_receiver_message_formats.md.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SatelliteFix:
    program: str
    platform_id: int
    satellite: str
    fixed_at: datetime
    loc_class: str
    latitude: float | None  # None for class Z: the pass is kept, the position is not
    longitude: float | None
    nb_messages: int
    battery_mv: int
    transmissions_total: int
    received_at: datetime  # when the batch carrying this row was delivered
    simulated: bool

    @property
    def key(self) -> tuple[int, datetime]:
        return (self.platform_id, self.fixed_at)


@dataclass(frozen=True)
class AcousticDetection:
    receiver_id: str
    transmitter_id: str
    detected_at: datetime
    received_at: datetime
    simulated: bool

    @property
    def key(self) -> tuple[str, str, datetime]:
        return (self.receiver_id, self.transmitter_id, self.detected_at)


@dataclass(frozen=True)
class ReceiverStatus:
    receiver_id: str
    status_at: datetime
    detections_total: int
    received_at: datetime
    simulated: bool

    @property
    def key(self) -> tuple[str, datetime]:
        return (self.receiver_id, self.status_at)
