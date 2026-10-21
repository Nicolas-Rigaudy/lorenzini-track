"""Sensitivity rules run on processed tracks before they are stored (item_003).

A rule takes a reconstructed track and returns the track to store: it may coarsen positions,
widen their error or drop points, but it must keep each point's `fixed_at`, which ties the
point back to its raw fix. Rules run in list order.

Two rules ship: `coarsen` snaps positions to a grid sized by IUCN status, and `embargo` drops
points newer than a publication delay. The policy values are proposals (decision 0010).
"""

import math
from collections.abc import Callable
from dataclasses import dataclass, replace
from datetime import datetime, timedelta

from app.processing.tracks import Track, TrackPoint
from app.simulator.geo import EARTH_RADIUS_KM

TrackRule = Callable[[Track], Track]

KM_PER_DEGREE = math.pi * EARTH_RADIUS_KM / 180.0


@dataclass(frozen=True)
class Precision:
    grid_degrees: float  # 0 keeps positions as they are
    delay_days: int  # publication delay


# assumption: stricter for more threatened species, after the OTN embargo rationale in 0004
POLICY: dict[str, Precision] = {
    "CR": Precision(grid_degrees=0.5, delay_days=730),
    "EN": Precision(grid_degrees=0.25, delay_days=365),
    "VU": Precision(grid_degrees=0.1, delay_days=180),
    "NT": Precision(grid_degrees=0.05, delay_days=90),
    "LC": Precision(grid_degrees=0.0, delay_days=0),
    "DD": Precision(grid_degrees=0.5, delay_days=730),
}


def precision_for(iucn_status: str) -> Precision:
    """Unknown status gets the strictest level."""
    return POLICY.get(iucn_status, POLICY["CR"])


def _map_points(track: Track, fn: Callable[[TrackPoint], TrackPoint | None]) -> Track:
    segments = []
    for segment in track.segments:
        kept = [q for q in (fn(p) for p in segment) if q is not None]
        if kept:
            segments.append(kept)
    return replace(track, segments=segments)


def coarsen(grid_degrees: float) -> TrackRule:
    """Snap each position to the centre of its grid cell; error grows to the cell half-diagonal."""

    def rule(track: Track) -> Track:
        if grid_degrees <= 0:
            return track

        def snap(p: TrackPoint) -> TrackPoint:
            lat = (math.floor(p.latitude / grid_degrees) + 0.5) * grid_degrees
            lon = (math.floor(p.longitude / grid_degrees) + 0.5) * grid_degrees
            half = grid_degrees / 2 * KM_PER_DEGREE
            half_diagonal = math.hypot(half, half * math.cos(math.radians(lat)))
            return replace(
                p,
                latitude=round(lat, 6),
                longitude=round(lon, 6),
                error_km=max(p.error_km, half_diagonal),
            )

        return _map_points(track, snap)

    return rule


def embargo(delay: timedelta, as_of: datetime) -> TrackRule:
    """Drop points fixed after `as_of - delay`."""
    cutoff = as_of - delay

    def rule(track: Track) -> Track:
        return _map_points(track, lambda p: p if p.fixed_at <= cutoff else None)

    return rule


def rules_for(iucn_status: str, as_of: datetime | None = None) -> list[TrackRule]:
    """The rule list for a species. The embargo is only added when a reference time is given."""
    level = precision_for(iucn_status)
    rules = [coarsen(level.grid_degrees)]
    if as_of is not None and level.delay_days:
        rules.append(embargo(timedelta(days=level.delay_days), as_of))
    return rules


# Rules applied when the pipeline is given none: the simulated fleet is scalloped hammerhead,
# critically endangered (IUCN 2019).
RULES: list[TrackRule] = rules_for("CR")


def apply_rules(track: Track, rules: list[TrackRule] | None = None) -> Track:
    for rule in RULES if rules is None else rules:
        track = rule(track)
    return track
