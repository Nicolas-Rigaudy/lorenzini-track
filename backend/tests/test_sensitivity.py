from datetime import UTC, datetime, timedelta

from app.processing.sensitivity import apply_rules, coarsen, embargo, precision_for, rules_for
from app.processing.tracks import Track, TrackPoint

T0 = datetime(2026, 1, 1, tzinfo=UTC)


def _track() -> Track:
    points = [
        TrackPoint(T0 + timedelta(days=d), -30.12 - d * 0.1, 153.37 + d * 0.1, "2", 1.0)
        for d in range(4)
    ]
    return Track(7, [points[:2], points[2:]], [])


def test_coarsen_snaps_to_cell_centres_and_widens_error():
    out = coarsen(0.5)(_track())
    for p in (p for s in out.segments for p in s):
        assert (p.latitude / 0.5) % 1 == 0.5 % 1 or abs((p.latitude / 0.5) % 1 - 0.5) < 1e-6
        assert abs((p.longitude / 0.5) % 1 - 0.5) < 1e-6
        assert p.error_km > 20


def test_coarsen_keeps_fixed_at_and_structure():
    before, out = _track(), coarsen(0.5)(_track())
    assert [[p.fixed_at for p in s] for s in out.segments] == [
        [p.fixed_at for p in s] for s in before.segments
    ]


def test_zero_grid_is_identity():
    assert coarsen(0)(_track()) == _track()


def test_embargo_drops_recent_points_and_empty_segments():
    out = embargo(timedelta(days=2), T0 + timedelta(days=3))(_track())
    assert [len(s) for s in out.segments] == [2]


def test_unknown_status_is_strictest():
    assert precision_for("??") == precision_for("CR")


def test_rules_for_adds_embargo_only_with_reference_time():
    assert len(rules_for("CR")) == 1
    assert len(rules_for("CR", T0)) == 2
    assert len(rules_for("LC", T0)) == 1


def test_default_rules_never_publish_finer_than_the_cell():
    out = apply_rules(_track())
    assert all(p.error_km > 20 for s in out.segments for p in s)
