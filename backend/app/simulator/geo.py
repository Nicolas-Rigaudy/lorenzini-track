"""Small geodesy helpers and a coarse land mask for the east coast of Australia."""

import itertools
import math

EARTH_RADIUS_KM = 6371.0088

# Hand-placed points on the outer coast (latitude, longitude), north to south, from
# Agnes Water (24 S) to Cape Howe (37.5 S). Good to roughly 10 km: enough to keep simulated
# sharks off the land, not a coastline for display.
COAST: tuple[tuple[float, float], ...] = (
    (-24.00, 151.95),
    (-25.00, 153.35),
    (-26.00, 153.15),
    (-27.00, 153.47),
    (-28.00, 153.45),
    (-28.64, 153.64),  # Byron Bay
    (-29.43, 153.36),  # Yamba
    (-30.30, 153.15),  # Coffs Harbour
    (-31.43, 152.93),  # Port Macquarie
    (-32.44, 152.54),  # Seal Rocks
    (-32.93, 151.80),  # Newcastle
    (-33.85, 151.29),  # Sydney
    (-34.42, 150.92),  # Wollongong
    (-35.10, 150.80),  # Jervis Bay
    (-36.20, 150.15),  # Narooma
    (-37.07, 149.95),  # Eden
    (-37.50, 149.98),  # Cape Howe
)
NORTH_LAT = COAST[0][0]
SOUTH_LAT = COAST[-1][0]


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def offset(lat: float, lon: float, east_km: float, north_km: float) -> tuple[float, float]:
    """Move a point by a local east/north displacement (equirectangular; fine below ~100 km)."""
    dlat = math.degrees(north_km / EARTH_RADIUS_KM)
    dlon = math.degrees(east_km / (EARTH_RADIUS_KM * math.cos(math.radians(lat))))
    return lat + dlat, lon + dlon


def coast_lon(lat: float) -> float:
    """Longitude of the coast at a latitude, linearly interpolated; clamped at the ends."""
    if lat >= NORTH_LAT:
        return COAST[0][1]
    if lat <= SOUTH_LAT:
        return COAST[-1][1]
    for (lat_n, lon_n), (lat_s, lon_s) in itertools.pairwise(COAST):
        if lat_s <= lat <= lat_n:
            f = (lat_n - lat) / (lat_n - lat_s)
            return lon_n + f * (lon_s - lon_n)
    raise AssertionError("unreachable")


def at_sea(lat: float, lon: float, buffer_km: float = 3.0) -> bool:
    """True if the point lies in the simulated domain, at least `buffer_km` east of the coast."""
    if not SOUTH_LAT <= lat <= NORTH_LAT:
        return False
    km_per_deg_lon = math.radians(1) * EARTH_RADIUS_KM * math.cos(math.radians(lat))
    return (lon - coast_lon(lat)) * km_per_deg_lon >= buffer_km
