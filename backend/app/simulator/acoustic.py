"""Acoustic receivers and the probability that a receiver hears a tag's ping.

Detection probability falls with distance along a logistic curve, the usual shape fitted to
range-test data (kessel2014). It is set by two distances: `d50_m`, where it is half the
near-receiver maximum, and `d05_m`, where it has fallen to 5% of that maximum. Range varies
widely between sites and over time (huveneers2016; kessel2014 recommends range tests in the
study area), so both are configuration, not constants. The defaults (400 m and 800 m) sit
between a coral-reef array where detection fell from 58% at 100 m to 26% at 200 m
(selby2016) and the 800-1,200 m open-water range Innovasea quotes for V16 tags on VR2W
receivers in good conditions (assumption: a coastal shelf curtain between the two).
"""

import math
import random
from dataclasses import dataclass

from app.simulator import geo


@dataclass(frozen=True)
class DetectionCurve:
    d50_m: float = 400.0
    d05_m: float = 800.0
    p_max: float = 0.95  # assumption: some pings are lost even next to a receiver

    @property
    def slope_per_m(self) -> float:
        # p(d05) / p_max = 1 / (1 + exp(k (d05 - d50))) = 0.05  =>  k = ln(19) / (d05 - d50)
        return math.log(19.0) / (self.d05_m - self.d50_m)

    def probability(self, distance_m: float) -> float:
        x = self.slope_per_m * (distance_m - self.d50_m)
        if x > 700:  # exp overflow; probability is 0 to double precision
            return 0.0
        return self.p_max / (1.0 + math.exp(x))

    @property
    def max_range_m(self) -> float:
        """Distance beyond which the probability is below 1e-4 and pings are not evaluated."""
        return self.d50_m + math.log(self.p_max / 1e-4 - 1.0) / self.slope_per_m

    def detects(self, rng: random.Random, distance_m: float) -> bool:
        return rng.random() < self.probability(distance_m)


@dataclass(frozen=True)
class Receiver:
    receiver_id: str
    line: str
    latitude: float
    longitude: float


def curtain(line: str, code: str, lat: float, start_lon: float, count: int, spacing_km: float):
    """A cross-shelf line of receivers running east from `start_lon` along `lat`."""
    receivers = []
    for i in range(count):
        r_lat, r_lon = geo.offset(lat, start_lon, i * spacing_km, 0.0)
        receivers.append(
            Receiver(f"LT-SIM-{code}-{i + 1:02d}", line, round(r_lat, 5), round(r_lon, 5))
        )
    return receivers


def default_array() -> list[Receiver]:
    """Two illustrative cross-shelf curtains off northern New South Wales.

    Modelled on the IMOS cross-shelf receiver lines; the positions are simulated, not real
    station coordinates.
    """
    return [
        *curtain("Coffs Harbour line", "COF", -30.30, 153.20, 20, 0.8),
        *curtain("Port Macquarie line", "PMQ", -31.45, 152.97, 20, 0.8),
    ]
