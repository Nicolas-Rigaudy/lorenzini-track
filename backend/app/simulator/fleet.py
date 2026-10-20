"""Run a simulated fleet: sharks, their tags, the receiver array and the raw messages.

Each shark carries a fin-mounted Argos satellite tag (in the style of a Wildlife Computers
SPOT tag) and an internal acoustic tag. The run produces, in memory, everything the writer in
`app.simulator.formats` turns into files: deployments, Argos locations with their delivery
batches, receiver uplinks (MQTT publishes) and the ground truth.

Satellite tag (parameters in `SatelliteTagParams`):
- The saltwater switch lets the tag transmit only while the fin is out of the water.
  Surfacings arrive as a Poisson process whose rate differs between sharks (lognormal across
  the fleet). Rate, spread and the chance a satellite is overhead are assumptions, calibrated
  so the share of days with at least one location spans what wells2018 reported for 26
  scalloped hammerheads with fin-mounted SPOT tags (8% to 100% of days, median 37%,
  interquartile range 25% to 47%; tests/test_simulator_fleet.py checks the median).
- A surfacing with a satellite overhead gives one Argos location, its class and error drawn
  as in `app.simulator.argos`.
- Up to 250 transmissions a day (the allotment wells2018 programmed), an optional duty cycle
  in UTC hours, a battery counted in transmissions, and an early failure (fouling, antenna
  damage) at an exponentially distributed time; heithaus2007 notes that fin-mounted tags
  often stop long before their battery would run out.
- Argos processes each location after a delay and delivers it in the next daily batch; a few
  locations are delivered again in the following batch, as re-processed Argos data is.

Acoustic tag and receivers (`AcousticTagParams`, `ReceiverParams`):
- The tag pings at random intervals until its battery, counted in pings, runs out.
- Each receiver within range hears a ping with the probability of `DetectionCurve`.
- Receivers uplink their detections over MQTT every 15 minutes, send a daily status, buffer
  through outages and publish the backlog when the link returns, and occasionally publish a
  message twice (MQTT QoS 1 delivers at least once).
"""

import bisect
import itertools
import math
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.simulator import argos, geo, rng
from app.simulator.acoustic import DetectionCurve, Receiver, default_array
from app.simulator.movement import MovementParams, TrackPoint, position_at, simulate_track

SPECIES_SCIENTIFIC = "Sphyrna lewini"
SPECIES_VERNACULAR = "Scalloped hammerhead"
ARGOS_SATELLITES = ("MB", "MC", "NK", "NN", "NP", "SR")
DAY = timedelta(days=1)


@dataclass(frozen=True)
class SatelliteTagParams:
    max_transmissions_per_day: int = 250  # wells2018
    battery_transmissions: int = 20_000  # assumption
    surfacings_per_day_median: float = 6.0  # assumption, calibrated to wells2018
    surfacings_per_day_log_sd: float = 1.0  # assumption, calibrated to wells2018
    transmissions_per_surfacing: tuple[int, int] = (1, 8)  # assumption
    satellite_overhead_probability: float = 0.08  # assumption, calibrated to wells2018
    failure_mean_days: float = 180.0  # assumption; heithaus2007 for early failure itself
    transmit_hours_utc: tuple[int, ...] = tuple(range(24))  # duty cycle: hours the tag may send
    battery_full_v: float = 3.6  # assumption: lithium primary cell
    battery_empty_v: float = 3.0  # assumption
    processing_delay_hours: tuple[float, float] = (0.25, 4.0)  # assumption
    redelivery_probability: float = 0.03  # assumption


@dataclass(frozen=True)
class AcousticTagParams:
    codespace: str = "A69-9001"
    ping_delay_s: tuple[float, float] = (60.0, 180.0)  # assumption: random-delay programme
    battery_pings: int = 1_500_000  # assumption: about 6.5 years at the mean delay


@dataclass(frozen=True)
class ReceiverParams:
    detection: DetectionCurve = field(default_factory=DetectionCurve)
    uplink_interval_minutes: int = 15
    uplink_latency_s: tuple[float, float] = (1.0, 20.0)  # assumption
    outage_probability_per_day: float = 0.02  # assumption
    outage_hours: tuple[float, float] = (6.0, 48.0)  # assumption
    duplicate_probability: float = 0.01  # assumption


@dataclass(frozen=True)
class FleetConfig:
    seed: int = 42
    sharks: int = 8
    start: datetime = datetime(2025, 11, 1, tzinfo=UTC)
    days: int = 365
    release_latitude: float = -30.25  # off Coffs Harbour, northern New South Wales
    release_longitude: float = 153.30
    release_radius_km: float = 8.0
    deployment_window_days: float = 14.0
    argos_program: str = "LT-SIM"
    argos_delivery_hour_utc: int = 6
    movement: MovementParams = field(default_factory=MovementParams)
    satellite_tag: SatelliteTagParams = field(default_factory=SatelliteTagParams)
    acoustic_tag: AcousticTagParams = field(default_factory=AcousticTagParams)
    receiver: ReceiverParams = field(default_factory=ReceiverParams)
    receivers: tuple[Receiver, ...] = field(default_factory=lambda: tuple(default_array()))

    @property
    def end(self) -> datetime:
        return self.start + self.days * DAY


@dataclass(frozen=True)
class Shark:
    shark_id: str
    deployed_at: datetime
    latitude: float
    longitude: float
    platform_id: int  # Argos platform (PTT) of the satellite tag
    transmitter_id: str  # acoustic tag code


@dataclass(frozen=True)
class ArgosLocation:
    platform_id: int
    satellite: str
    loc_date: datetime
    loc_class: str
    latitude: float | None
    longitude: float | None
    nb_messages: int
    battery_mv: int
    transmissions_total: int
    true_latitude: float
    true_longitude: float
    error_km: float | None
    available_at: datetime


@dataclass(frozen=True)
class Detection:
    receiver_id: str
    transmitter_id: str
    detected_at: datetime
    distance_m: float


@dataclass(frozen=True)
class Publish:
    published_at: datetime
    topic: str
    payload: dict


@dataclass(frozen=True)
class TagFate:
    tag_id: str
    kind: str  # "argos" or "acoustic"
    shark_id: str
    ended_at: datetime
    reason: str  # "battery", "failure" or "end_of_run"
    messages: int  # transmissions (argos) or pings (acoustic) sent


@dataclass
class FleetRun:
    config: FleetConfig
    sharks: list[Shark]
    tracks: dict[str, list[TrackPoint]]
    argos_locations: list[ArgosLocation]
    argos_deliveries: dict[datetime, list[ArgosLocation]]
    detections: list[Detection]
    publishes: list[Publish]
    fates: list[TagFate]


def _deploy(config: FleetConfig, index: int) -> Shark:
    r = rng.stream(config.seed, "deployment", index)
    deployed_at = config.start + timedelta(
        minutes=round(r.uniform(0.0, config.deployment_window_days) * 24 * 60)
    )
    while True:
        distance = config.release_radius_km * math.sqrt(r.random())
        bearing = r.uniform(0.0, 2 * math.pi)
        lat, lon = geo.offset(
            config.release_latitude,
            config.release_longitude,
            distance * math.sin(bearing),
            distance * math.cos(bearing),
        )
        if geo.at_sea(lat, lon, config.movement.coast_buffer_km):
            break
    return Shark(
        shark_id=f"LT-SIM-SL{index + 1:02d}",
        deployed_at=deployed_at,
        latitude=lat,
        longitude=lon,
        platform_id=990001 + index,
        transmitter_id=f"{config.acoustic_tag.codespace}-{60001 + index}",
    )


def _battery_mv(params: SatelliteTagParams, remaining: int) -> int:
    fraction = remaining / params.battery_transmissions
    volts = params.battery_empty_v + fraction * (params.battery_full_v - params.battery_empty_v)
    return round(volts * 1000)


def _simulate_argos_tag(
    config: FleetConfig, shark: Shark, track: list[TrackPoint]
) -> tuple[list[ArgosLocation], TagFate]:
    params = config.satellite_tag
    r = rng.stream(config.seed, "argos-tag", shark.shark_id)
    rate = params.surfacings_per_day_median * math.exp(
        r.gauss(0.0, params.surfacings_per_day_log_sd)
    )
    failure_at = shark.deployed_at + r.expovariate(1.0 / params.failure_mean_days) * DAY
    end = min(config.end, failure_at)
    hours = set(params.transmit_hours_utc)
    battery = params.battery_transmissions
    sent_total = 0
    sent_today: dict[object, int] = {}
    locations: list[ArgosLocation] = []
    t = shark.deployed_at
    reason = "failure" if failure_at < config.end else "end_of_run"
    ended_at = end
    while True:
        t = t + r.expovariate(rate) * DAY
        if t >= end:
            break
        t = t.replace(microsecond=0)
        if t.hour not in hours:
            continue
        day = t.date()
        allowance = params.max_transmissions_per_day - sent_today.get(day, 0)
        if allowance <= 0:
            continue
        n = min(r.randint(*params.transmissions_per_surfacing), allowance, battery)
        battery -= n
        sent_total += n
        sent_today[day] = sent_today.get(day, 0) + n
        if r.random() < params.satellite_overhead_probability:
            true_lat, true_lon = position_at(track, t)
            lc = argos.draw_class(r)
            if lc == "Z":
                lat = lon = error_km = None
            else:
                east, north = argos.draw_error_km(r, lc)
                lat, lon = geo.offset(true_lat, true_lon, east, north)
                error_km = math.hypot(east, north)
            delay = r.uniform(*params.processing_delay_hours)
            locations.append(
                ArgosLocation(
                    platform_id=shark.platform_id,
                    satellite=r.choice(ARGOS_SATELLITES),
                    loc_date=t,
                    loc_class=lc,
                    latitude=lat,
                    longitude=lon,
                    nb_messages=n,
                    battery_mv=_battery_mv(params, battery),
                    transmissions_total=sent_total,
                    true_latitude=true_lat,
                    true_longitude=true_lon,
                    error_km=error_km,
                    available_at=t + timedelta(hours=delay),
                )
            )
        if battery == 0:
            reason, ended_at = "battery", t
            break
    fate = TagFate(str(shark.platform_id), "argos", shark.shark_id, ended_at, reason, sent_total)
    return locations, fate


def _deliveries(
    config: FleetConfig, locations: list[ArgosLocation]
) -> dict[datetime, list[ArgosLocation]]:
    """Daily Argos batches. Each location goes in the first batch after it is processed; some
    are delivered again, unchanged, in the batch after that."""
    first = config.start.replace(hour=config.argos_delivery_hour_utc)
    r = rng.stream(config.seed, "argos-delivery")
    batches: dict[datetime, list[ArgosLocation]] = {}
    for loc in sorted(locations, key=lambda x: (x.loc_date, x.platform_id)):
        k = max(0, math.ceil((loc.available_at - first) / DAY))
        batch = first + k * DAY
        batches.setdefault(batch, []).append(loc)
        if r.random() < config.satellite_tag.redelivery_probability:
            batches.setdefault(batch + DAY, []).append(loc)
    return {
        when: sorted(batch, key=lambda x: (x.platform_id, x.loc_date))
        for when, batch in sorted(batches.items())
    }


def _candidate_receivers(
    config: FleetConfig, track: list[TrackPoint], max_range_km: float
) -> list[tuple[Receiver, ...]]:
    """For each track step, the receivers that could hear the tag somewhere along it.

    Every point on a step lies within one step length of its start, so a receiver further
    than (step length + range) from the start cannot hear any ping sent during the step."""
    candidates = []
    for a, b in itertools.pairwise(track):
        reach = geo.haversine_km(a.latitude, a.longitude, b.latitude, b.longitude) + max_range_km
        candidates.append(
            tuple(
                rc
                for rc in config.receivers
                if geo.haversine_km(a.latitude, a.longitude, rc.latitude, rc.longitude) <= reach
            )
        )
    return candidates


def _simulate_acoustic_tag(
    config: FleetConfig, shark: Shark, track: list[TrackPoint]
) -> tuple[list[Detection], TagFate]:
    params = config.acoustic_tag
    curve = config.receiver.detection
    max_range_km = curve.max_range_m / 1000.0
    pings_rng = rng.stream(config.seed, "acoustic-pings", shark.shark_id)
    detect_rng = rng.stream(config.seed, "acoustic-detections", shark.shark_id)
    candidates = _candidate_receivers(config, track, max_range_km)
    # Ping times are kept as seconds since deployment: the loop runs about 260,000 times per
    # tag-year, and only pings near a receiver need a datetime.
    step_s = (track[1].time - track[0].time).total_seconds()
    end_s = (config.end - shark.deployed_at).total_seconds()
    low, high = params.ping_delay_s
    detections: list[Detection] = []
    t_s = 0.0
    pings = 0
    reason, ended_at = "end_of_run", config.end
    while True:
        t_s += pings_rng.uniform(low, high)
        if t_s >= end_s:
            break
        pings += 1
        nearby = candidates[min(int(t_s / step_s), len(candidates) - 1)]
        if nearby:
            when = shark.deployed_at + timedelta(seconds=t_s)
            lat, lon = position_at(track, when)
            for rc in nearby:
                d_km = geo.haversine_km(lat, lon, rc.latitude, rc.longitude)
                if d_km <= max_range_km and curve.detects(detect_rng, d_km * 1000.0):
                    detections.append(
                        Detection(
                            rc.receiver_id,
                            shark.transmitter_id,
                            when.replace(microsecond=0),
                            d_km * 1000.0,
                        )
                    )
        if pings == params.battery_pings:
            reason = "battery"
            ended_at = (shark.deployed_at + timedelta(seconds=t_s)).replace(microsecond=0)
            break
    fate = TagFate(shark.transmitter_id, "acoustic", shark.shark_id, ended_at, reason, pings)
    return detections, fate


def _iso(when: datetime) -> str:
    return when.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _outages(config: FleetConfig, r: random.Random) -> list[tuple[datetime, datetime]]:
    params = config.receiver
    spans: list[tuple[datetime, datetime]] = []
    for day in range(config.days):
        if r.random() < params.outage_probability_per_day:
            begin = config.start + day * DAY + timedelta(seconds=round(r.uniform(0, 86400)))
            length = timedelta(seconds=round(r.uniform(*params.outage_hours) * 3600))
            if spans and begin <= spans[-1][1]:
                spans[-1] = (spans[-1][0], max(spans[-1][1], begin + length))
            else:
                spans.append((begin, begin + length))
    return spans


def _send_time(spans: list[tuple[datetime, datetime]], when: datetime) -> datetime:
    """When a message due at `when` actually leaves the receiver: at once, or when an outage
    covering `when` ends."""
    i = bisect.bisect_right([s[0] for s in spans], when) - 1
    if i >= 0 and spans[i][0] <= when < spans[i][1]:
        return spans[i][1]
    return when


def _receiver_publishes(
    config: FleetConfig, receiver: Receiver, detections: list[Detection]
) -> list[Publish]:
    params = config.receiver
    r = rng.stream(config.seed, "receiver", receiver.receiver_id)
    spans = _outages(config, r)
    interval = timedelta(minutes=params.uplink_interval_minutes)
    # Messages the receiver means to send, in the order it queues them.
    due: list[tuple[datetime, str, dict]] = []
    by_window: dict[int, list[Detection]] = {}
    for det in detections:
        by_window.setdefault(int((det.detected_at - config.start) / interval), []).append(det)
    for window, dets in sorted(by_window.items()):
        due.append(
            (
                config.start + (window + 1) * interval,
                "detections",
                {
                    "detections": [
                        {"detected_at": _iso(d.detected_at), "transmitter_id": d.transmitter_id}
                        for d in sorted(dets, key=lambda d: (d.detected_at, d.transmitter_id))
                    ]
                },
            )
        )
    total = 0
    counts = sorted(d.detected_at for d in detections)
    for day in range(1, config.days + 1):
        status_at = config.start + day * DAY
        total = bisect.bisect_left(counts, status_at)
        due.append((status_at, "status", {"status_at": _iso(status_at), "detections_total": total}))
    due.sort(key=lambda m: (m[0], m[1]))

    publishes: list[Publish] = []
    for seq, (when, kind, body) in enumerate(due, start=1):
        sent_at = _send_time(spans, when)
        payload = {
            "format": f"lt-receiver-{kind}/1",
            "receiver_id": receiver.receiver_id,
            "seq": seq,
            "sent_at": _iso(sent_at),
            "simulated": True,
            **body,
        }
        topic = f"lorenzini/sim/receivers/{receiver.receiver_id}/{kind}"
        published_at = sent_at + timedelta(seconds=round(r.uniform(*params.uplink_latency_s)))
        publishes.append(Publish(published_at, topic, payload))
        if r.random() < params.duplicate_probability:
            again = published_at + timedelta(seconds=round(r.uniform(1.0, 30.0)))
            publishes.append(Publish(again, topic, payload))
    return publishes


def run(config: FleetConfig) -> FleetRun:
    sharks = [_deploy(config, i) for i in range(config.sharks)]
    tracks: dict[str, list[TrackPoint]] = {}
    locations: list[ArgosLocation] = []
    detections: list[Detection] = []
    fates: list[TagFate] = []
    step = timedelta(hours=config.movement.step_hours)
    for shark in sharks:
        steps = math.ceil((config.end - shark.deployed_at) / step)
        track = simulate_track(
            rng.stream(config.seed, "movement", shark.shark_id),
            shark.deployed_at,
            shark.latitude,
            shark.longitude,
            steps,
            config.movement,
        )
        tracks[shark.shark_id] = track
        locs, fate = _simulate_argos_tag(config, shark, track)
        locations.extend(locs)
        fates.append(fate)
        dets, fate = _simulate_acoustic_tag(config, shark, track)
        detections.extend(dets)
        fates.append(fate)
    detections.sort(key=lambda d: (d.receiver_id, d.detected_at, d.transmitter_id))
    publishes: list[Publish] = []
    for receiver in config.receivers:
        mine = [d for d in detections if d.receiver_id == receiver.receiver_id]
        publishes.extend(_receiver_publishes(config, receiver, mine))
    publishes.sort(key=lambda p: (p.published_at, p.topic, p.payload["seq"]))
    return FleetRun(
        config=config,
        sharks=sharks,
        tracks=tracks,
        argos_locations=sorted(locations, key=lambda x: (x.platform_id, x.loc_date)),
        argos_deliveries=_deliveries(config, locations),
        detections=detections,
        publishes=publishes,
        fates=fates,
    )
