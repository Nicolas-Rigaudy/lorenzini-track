"""AC3: the acoustic detection rate falls with distance to the receiver as configured."""

import itertools
import random

import pytest

from app.simulator.acoustic import DetectionCurve, default_array

DISTANCES_M = (50, 200, 400, 600, 800, 1000, 1200)


@pytest.mark.parametrize(
    "curve", [DetectionCurve(), DetectionCurve(d50_m=150, d05_m=350, p_max=0.8)]
)
def test_curve_meets_its_configured_distances(curve):
    assert curve.probability(curve.d50_m) == pytest.approx(curve.p_max / 2)
    assert curve.probability(curve.d05_m) == pytest.approx(curve.p_max * 0.05)
    assert curve.probability(curve.max_range_m) == pytest.approx(1e-4)
    probabilities = [curve.probability(d) for d in range(0, 3000, 10)]
    assert all(a > b for a, b in itertools.pairwise(probabilities))


@pytest.mark.parametrize(
    "curve", [DetectionCurve(), DetectionCurve(d50_m=150, d05_m=350, p_max=0.8)]
)
def test_detection_rate_falls_with_distance_as_configured(curve):
    r = random.Random(7)
    n = 20_000
    rates = [sum(curve.detects(r, d) for _ in range(n)) / n for d in DISTANCES_M]
    assert all(a > b for a, b in itertools.pairwise(rates) if a > 0.01)
    for d, rate in zip(DISTANCES_M, rates, strict=True):
        assert rate == pytest.approx(curve.probability(d), abs=0.015)


def test_a_shorter_configured_range_detects_less():
    r1, r2 = random.Random(3), random.Random(3)
    wide, narrow = DetectionCurve(), DetectionCurve(d50_m=150, d05_m=350)
    n = 10_000
    assert (
        sum(narrow.detects(r2, 300) for _ in range(n))
        < sum(wide.detects(r1, 300) for _ in range(n)) / 2
    )


def test_default_array_has_two_lines_of_unique_receivers():
    receivers = default_array()
    assert len({rc.receiver_id for rc in receivers}) == len(receivers) == 40
    assert {rc.line for rc in receivers} == {"Coffs Harbour line", "Port Macquarie line"}
