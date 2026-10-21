"""Hook where item_003's sensitivity rules run on processed tracks, before they are stored.

A rule takes a reconstructed track and returns the track to store: it may coarsen positions,
widen their error or drop points, but it must keep each point's `fixed_at`, which ties the
point back to its raw fix. Rules run in list order. The list is empty until item_003 decides
the rules.
"""

from collections.abc import Callable

from app.processing.tracks import Track

TrackRule = Callable[[Track], Track]

RULES: list[TrackRule] = []


def apply_rules(track: Track, rules: list[TrackRule] | None = None) -> Track:
    for rule in RULES if rules is None else rules:
        track = rule(track)
    return track
