"""Shark movement: a behavioural-state switching correlated random walk (DCRWS).

The model is the first-difference correlated random walk with switching of jonsen2005, the
model wells2018 fitted to scalloped hammerheads tracked with fin-mounted SPOT tags, at the
same 12-hour time step:

    d_t = gamma_b * R(theta_b) * d_(t-1) + e_t,    e_t ~ N(0, sigma^2 I)

where d_t is the displacement over step t, b the behavioural state at the start of the step
(transit or area-restricted search, ARS), R a rotation, and the states switch as a Markov
chain. Between steps the true position is interpolated linearly.

Parameters:
- ARS gamma 0.08: the mean move persistence wells2018 estimated for scalloped hammerheads,
  which they describe as tortuous, area-restricted movement.
- Transit gamma 0.8, turning angles 0 and the switching probabilities: assumptions. wells2018
  could not separate behavioural modes for most hammerheads, so no hammerhead fit gives them.
- sigma 9.8 km: set so the mean distance covered is about 28 km per day, the rate of the one
  long scalloped hammerhead track with published distance and duration (salinas2025:
  5,783 km in 204 days, 28.3 km/day). tests/test_simulator_movement.py checks it.
"""

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from app.simulator import geo

TRANSIT = "transit"
ARS = "ars"


@dataclass(frozen=True)
class MovementParams:
    step_hours: float = 12.0  # wells2018
    gamma_transit: float = 0.8  # assumption
    gamma_ars: float = 0.08  # wells2018
    theta_transit: float = 0.0  # assumption
    theta_ars: float = 0.0  # assumption
    sigma_km: float = 9.8  # calibrated to salinas2025
    p_stay_transit: float = 0.8  # assumption
    p_stay_ars: float = 0.9  # assumption
    coast_buffer_km: float = 3.0


@dataclass(frozen=True)
class TrackPoint:
    time: datetime
    latitude: float
    longitude: float
    state: str


def _rotate(x: float, y: float, theta: float) -> tuple[float, float]:
    c, s = math.cos(theta), math.sin(theta)
    return c * x - s * y, s * x + c * y


def simulate_track(
    rng: random.Random,
    start: datetime,
    latitude: float,
    longitude: float,
    steps: int,
    params: MovementParams,
) -> list[TrackPoint]:
    """True positions at each step. A step that would reach land is drawn again (up to 20
    times); if it still would, the shark stays put for that step."""
    state = ARS if rng.random() < 0.5 else TRANSIT
    gamma = params.gamma_ars if state == ARS else params.gamma_transit
    spread = params.sigma_km / math.sqrt(1.0 - gamma**2)  # stationary spread for the state
    dx, dy = rng.gauss(0.0, spread), rng.gauss(0.0, spread)
    lat, lon = latitude, longitude
    track = [TrackPoint(start, lat, lon, state)]
    step = timedelta(hours=params.step_hours)
    for i in range(1, steps + 1):
        if state == TRANSIT:
            gamma, theta = params.gamma_transit, params.theta_transit
        else:
            gamma, theta = params.gamma_ars, params.theta_ars
        px, py = _rotate(dx, dy, theta)
        for _ in range(20):
            nx = gamma * px + rng.gauss(0.0, params.sigma_km)
            ny = gamma * py + rng.gauss(0.0, params.sigma_km)
            n_lat, n_lon = geo.offset(lat, lon, nx, ny)
            if geo.at_sea(n_lat, n_lon, params.coast_buffer_km):
                dx, dy, lat, lon = nx, ny, n_lat, n_lon
                break
        else:
            dx, dy = 0.0, 0.0
        stay = params.p_stay_transit if state == TRANSIT else params.p_stay_ars
        if rng.random() >= stay:
            state = ARS if state == TRANSIT else TRANSIT
        track.append(TrackPoint(start + i * step, lat, lon, state))
    return track


def position_at(track: list[TrackPoint], when: datetime) -> tuple[float, float]:
    """True position at any time inside the track, interpolated linearly between steps."""
    step = track[1].time - track[0].time
    i = int((when - track[0].time) / step)
    i = min(max(i, 0), len(track) - 2)
    a, b = track[i], track[i + 1]
    f = (when - a.time) / step
    return a.latitude + f * (b.latitude - a.latitude), a.longitude + f * (b.longitude - a.longitude)
