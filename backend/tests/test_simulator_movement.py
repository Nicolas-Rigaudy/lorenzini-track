"""Movement model: cited parameters, land avoidance and determinism of the track."""

import itertools
from datetime import UTC, datetime

import pytest

from app.simulator import geo, movement, rng

START = datetime(2025, 11, 1, tzinfo=UTC)


def track(seed: int, params: movement.MovementParams, steps: int = 730, lon: float = 153.30):
    return movement.simulate_track(rng.stream(seed, "m"), START, -30.25, lon, steps, params)


def km_per_day(points) -> float:
    total = sum(
        geo.haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
        for a, b in itertools.pairwise(points)
    )
    return total / (len(points) - 1) * 2  # two 12-hour steps a day


def test_mean_daily_distance_matches_the_long_hammerhead_track():
    # salinas2025: 5,783 km in 204 days, 28.3 km/day.
    params = movement.MovementParams()
    rates = [km_per_day(track(seed, params)) for seed in range(20)]
    assert sum(rates) / len(rates) == pytest.approx(28.3, rel=0.10)


def test_tracks_stay_at_sea():
    for seed in range(10):
        for p in track(seed, movement.MovementParams()):
            assert geo.at_sea(p.latitude, p.longitude)


def test_transit_is_more_directed_than_area_restricted_search():
    def straightness(params):
        # Offshore, so the coast does not deflect the track; averaged over seeds.
        ratios = []
        for seed in range(20):
            points = track(seed, params, steps=60, lon=156.0)
            path = km_per_day(points) * 30
            a, b = points[0], points[-1]
            ratios.append(geo.haversine_km(a.latitude, a.longitude, b.latitude, b.longitude) / path)
        return sum(ratios) / len(ratios)

    transit = movement.MovementParams(p_stay_transit=1.0, p_stay_ars=0.0)
    ars = movement.MovementParams(p_stay_transit=0.0, p_stay_ars=1.0)
    assert straightness(transit) > straightness(ars)


def test_same_stream_gives_the_same_track():
    params = movement.MovementParams()
    assert track(9, params) == track(9, params)
    assert track(9, params) != track(10, params)


def test_position_at_interpolates_between_steps():
    points = track(1, movement.MovementParams(), steps=4)
    a, b = points[1], points[2]
    lat, lon = movement.position_at(points, a.time + (b.time - a.time) / 2)
    assert lat == pytest.approx((a.latitude + b.latitude) / 2)
    assert lon == pytest.approx((a.longitude + b.longitude) / 2)
