from datetime import datetime, timedelta, timezone
import pytest
from domain import (RuleViolation, ZURICH, cancellation_review, local_time, overlaps,
                    parse, stamp, window)


def test_touching_intervals_do_not_overlap():
    t = local_time("2026-11-10 09:00")
    assert not overlaps(t, t + timedelta(hours=2), t + timedelta(hours=2), t + timedelta(hours=3))
    assert overlaps(t, t + timedelta(hours=2), t + timedelta(minutes=119), t + timedelta(hours=3))


def test_cross_midnight_overlap():
    assert overlaps(local_time("2026-11-10 23:00"), local_time("2026-11-11 01:00"),
                    local_time("2026-11-11 00:30"), local_time("2026-11-11 02:00"))


@pytest.mark.parametrize("hours,flag", [(47.999, True), (48, False), (48.001, False), (-1, True)])
def test_exact_48_hour_policy_boundary(hours, flag):
    requested = local_time("2026-11-09 08:00")
    assert cancellation_review(requested + timedelta(hours=hours), requested) is flag


def test_spring_boundary_uses_elapsed_hours_not_wall_clock():
    request = local_time("2026-03-28 10:00")
    # Wall-clock difference is 48h, but the elapsed UTC duration is 47h.
    assert cancellation_review(local_time("2026-03-30 10:00"), request)
    assert not cancellation_review(local_time("2026-03-30 11:00"), request)


def test_autumn_boundary_uses_elapsed_hours():
    request = local_time("2026-10-24 10:00")
    assert not cancellation_review(local_time("2026-10-26 09:00"), request)


@pytest.mark.parametrize("wall,word", [("2026-03-29 02:30", "inexistante"), ("2026-10-25 02:30", "ambiguë")])
def test_dst_gap_and_ambiguous_local_input_refused(wall, word):
    with pytest.raises(RuleViolation, match=word):
        local_time(wall)


def test_explicit_dst_offsets_represent_distinct_instants():
    a = parse("2026-10-25T02:30:00+02:00")
    b = parse("2026-10-25T02:30:00+01:00")
    assert b - a == timedelta(hours=1)
    assert stamp(a) != stamp(b)


def test_imaginary_aware_time_and_naive_input_refused():
    with pytest.raises(RuleViolation):
        stamp(datetime(2026, 3, 29, 2, 30, tzinfo=ZURICH))
    with pytest.raises(RuleViolation, match="sans fuseau"):
        stamp(datetime(2026, 11, 10, 9))


def test_reversed_and_zero_duration_windows_refused():
    t = local_time("2026-11-10 09:00")
    with pytest.raises(RuleViolation):
        window(t, t)
    with pytest.raises(RuleViolation):
        window(t, t - timedelta(minutes=1))


def test_utc_storage_normalizes_offset():
    assert stamp(local_time("2026-11-10 09:00")) == "2026-11-10T08:00:00+00:00"
