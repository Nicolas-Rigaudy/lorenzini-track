"""AC2: Argos error by location class and the share of each class match the cited sources."""

import math
import random

import pytest

from app.simulator import argos


def p68(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[int(0.68 * len(ordered))]


def test_class_shares_add_up_and_reproduce_the_grouped_shares():
    assert math.isclose(sum(argos.CLASS_SHARES.values()), 1.0)
    shares = argos.CLASS_SHARES
    assert math.isclose(shares["3"] + shares["2"] + shares["1"], 0.54)  # anderson2025
    assert math.isclose(shares["A"] + shares["B"], 0.35)  # anderson2025
    assert shares["Z"] < 0.01  # anderson2025: "<1%"


def test_drawn_class_shares_match_the_sources():
    r = random.Random(1)
    n = 50_000
    draws = [argos.draw_class(r) for _ in range(n)]
    share = {lc: draws.count(lc) / n for lc in argos.CLASSES}
    # Grouped shares from anderson2025, within 2 percentage points of sampling noise.
    assert share["3"] + share["2"] + share["1"] == pytest.approx(0.54, abs=0.02)
    assert share["A"] + share["B"] == pytest.approx(0.35, abs=0.02)
    assert share["0"] == pytest.approx(0.105, abs=0.02)
    assert share["Z"] < 0.01
    # Split inside each group from costa2010's class counts.
    counts = argos.COSTA_CLASS_COUNTS
    high = share["3"] + share["2"] + share["1"]
    for lc in ("3", "2", "1"):
        assert share[lc] / high == pytest.approx(counts[lc] / 391, abs=0.03)
    assert share["B"] / (share["A"] + share["B"]) == pytest.approx(336 / 528, abs=0.03)


@pytest.mark.parametrize("lc", argos.POSITIONED)
def test_error_68th_percentile_is_within_the_published_range(lc):
    r = random.Random(f"error-{lc}")
    errors = [math.hypot(*argos.draw_error_km(r, lc)) for _ in range(20_000)]
    low, high = argos.ERROR_P68_RANGE_KM[lc]  # costa2010 and Hazel 2009 (costa2010 Table 4)
    assert low * 0.95 <= p68(errors) <= high * 1.05
    assert p68(errors) == pytest.approx(argos.ERROR_P68_KM[lc], rel=0.05)


def test_class_3_log_mean_reproduces_costa_table_2():
    assert argos.error_log_mean("3") == pytest.approx(-1.198, abs=0.002)


def test_error_grows_from_class_3_to_class_b():
    p68s = [argos.ERROR_P68_KM[lc] for lc in argos.POSITIONED]
    assert p68s == sorted(p68s)
