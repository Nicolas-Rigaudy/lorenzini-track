"""Argos location classes: how often each class occurs, and how far off each class is.

Error by class (costa2010): at-sea errors measured on tags carrying both Argos and Fastloc
GPS. Each class's error distance is lognormal; the shape `s` is Costa et al.'s fitted value
(Table 2) and the scale is set so the 68th percentile equals their measured 68th percentile
(Table 4, "this study"). For class 3 this reproduces their fitted log-mean (-1.198).

Share of each class: fin-mounted shark tags (anderson2025, porbeagle, 38 tags, 11,999 Argos
locations): 54% in classes 1-3, 35% in A or B, under 1% Z, so about 11% class 0. Within
those groups the split follows the class counts of Costa et al.'s comparison set (Table 2),
since anderson2025 gives the per-class counts only in a supplementary table.

Class Z is an invalid location: the record keeps the pass but carries no coordinates
(heithaus2007 describes Z as uplinks for which no position can be calculated).
"""

import math
import random
from statistics import NormalDist

CLASSES: tuple[str, ...] = ("3", "2", "1", "0", "A", "B", "Z")
POSITIONED: tuple[str, ...] = CLASSES[:-1]

# 68th-percentile error distance in km, costa2010 Table 4 ("this study", on animals at sea).
ERROR_P68_KM: dict[str, float] = {
    "3": 0.486,
    "2": 1.011,
    "1": 1.201,
    "0": 4.182,
    "A": 6.185,
    "B": 10.276,
}
# Lognormal shape of the error distance per class, costa2010 Table 2.
ERROR_LOG_SD: dict[str, float] = {
    "3": 1.02,
    "2": 0.693,
    "1": 0.712,
    "0": 0.521,
    "A": 0.506,
    "B": 0.612,
}
# The other at-sea animal study with distance errors that costa2010 Table 4 lists
# (Hazel 2009, green turtles). Together with ERROR_P68_KM it bounds the published range.
HAZEL_P68_KM: dict[str, float] = {
    "3": 0.482,
    "2": 0.785,
    "1": 1.430,
    "0": 5.179,
    "A": 8.072,
    "B": 11.484,
}
ERROR_P68_RANGE_KM: dict[str, tuple[float, float]] = {
    lc: (min(ERROR_P68_KM[lc], HAZEL_P68_KM[lc]), max(ERROR_P68_KM[lc], HAZEL_P68_KM[lc]))
    for lc in POSITIONED
}

# Group shares, anderson2025. Z is reported as "<1%"; the simulator uses half of that bound.
SHARE_CLASSES_1_TO_3 = 0.54
SHARE_CLASSES_A_B = 0.35
SHARE_CLASS_Z = 0.005
SHARE_CLASS_0 = 1.0 - SHARE_CLASSES_1_TO_3 - SHARE_CLASSES_A_B - SHARE_CLASS_Z
# Class counts in costa2010's Argos/GPS comparison set (Table 2, sample sizes).
COSTA_CLASS_COUNTS: dict[str, int] = {"3": 33, "2": 107, "1": 251, "0": 167, "A": 192, "B": 336}


def _class_shares() -> dict[str, float]:
    high = sum(COSTA_CLASS_COUNTS[lc] for lc in ("3", "2", "1"))
    low = sum(COSTA_CLASS_COUNTS[lc] for lc in ("A", "B"))
    shares = {lc: SHARE_CLASSES_1_TO_3 * COSTA_CLASS_COUNTS[lc] / high for lc in ("3", "2", "1")}
    shares["0"] = SHARE_CLASS_0
    shares.update({lc: SHARE_CLASSES_A_B * COSTA_CLASS_COUNTS[lc] / low for lc in ("A", "B")})
    shares["Z"] = SHARE_CLASS_Z
    return shares


CLASS_SHARES: dict[str, float] = _class_shares()

_Z68 = NormalDist().inv_cdf(0.68)


def error_log_mean(lc: str) -> float:
    """Log-mean (km) of the lognormal error distance for a class."""
    return math.log(ERROR_P68_KM[lc]) - _Z68 * ERROR_LOG_SD[lc]


def draw_class(rng: random.Random) -> str:
    return rng.choices(CLASSES, weights=[CLASS_SHARES[lc] for lc in CLASSES])[0]


def draw_error_km(rng: random.Random, lc: str) -> tuple[float, float]:
    """East and north error (km) for a positioned class. Bearing is uniform (isotropic)."""
    distance = rng.lognormvariate(error_log_mean(lc), ERROR_LOG_SD[lc])
    bearing = rng.uniform(0.0, 2 * math.pi)
    return distance * math.sin(bearing), distance * math.cos(bearing)
