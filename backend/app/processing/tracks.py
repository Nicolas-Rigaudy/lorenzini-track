"""Quality filtering and track reconstruction for satellite fixes.

Fixes are filtered per platform in time order: class Z (no position) is dropped, and a fix is
rejected when reaching it from the last accepted fix needs a speed above `max_speed_kmh`.
Argos error is allowed for before judging speed: the distance between two fixes is reduced by
the 68th-percentile error of both (costa2010, the same values the simulator draws from), so a
class B fix 8 km off is not mistaken for a shark swimming at 60 km/h.

Track reconstruction keeps gaps as gaps: a pause longer than `gap_hours` between accepted fixes
starts a new segment instead of drawing a straight line across it. Every point keeps its
location class so the map can draw the uncertainty of each position.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta

from app.gateway.messages import SatelliteFix
from app.simulator.argos import ERROR_P68_KM
from app.simulator.geo import haversine_km


@dataclass(frozen=True)
class ProcessingParams:
    # assumption: scalloped hammerheads cruise near 2-4 km/h and burst a few times faster
    max_speed_kmh: float = 12.0
    gap_hours: float = 48.0  # assumption: longer than two days without a fix is a gap


@dataclass(frozen=True)
class TrackPoint:
    fixed_at: datetime
    latitude: float
    longitude: float
    loc_class: str
    error_km: float  # 68th-percentile radius for the class


@dataclass(frozen=True)
class Track:
    platform_id: int
    segments: list[list[TrackPoint]]
    rejected: list[SatelliteFix]  # dropped by the speed filter, kept for the raw view


def _speed_kmh(a: SatelliteFix, b: SatelliteFix) -> float:
    hours = (b.fixed_at - a.fixed_at).total_seconds() / 3600.0
    distance = haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
    distance = max(0.0, distance - ERROR_P68_KM[a.loc_class] - ERROR_P68_KM[b.loc_class])
    return distance / hours if hours > 0 else float("inf")


def reconstruct(fixes: list[SatelliteFix], params: ProcessingParams | None = None) -> list[Track]:
    params = params or ProcessingParams()
    by_platform: dict[int, list[SatelliteFix]] = {}
    for fix in sorted(fixes, key=lambda f: (f.platform_id, f.fixed_at)):
        if fix.latitude is not None:
            by_platform.setdefault(fix.platform_id, []).append(fix)
    tracks = []
    for platform_id, platform_fixes in sorted(by_platform.items()):
        accepted: list[SatelliteFix] = []
        rejected: list[SatelliteFix] = []
        for fix in platform_fixes:
            if accepted and _speed_kmh(accepted[-1], fix) > params.max_speed_kmh:
                rejected.append(fix)
            else:
                accepted.append(fix)
        segments: list[list[TrackPoint]] = []
        previous = None
        for fix in accepted:
            if previous is None or (fix.fixed_at - previous.fixed_at) > timedelta(
                hours=params.gap_hours
            ):
                segments.append([])
            segments[-1].append(
                TrackPoint(
                    fix.fixed_at,
                    fix.latitude,
                    fix.longitude,
                    fix.loc_class,
                    ERROR_P68_KM[fix.loc_class],
                )
            )
            previous = fix
        tracks.append(Track(platform_id, segments, rejected))
    return tracks
