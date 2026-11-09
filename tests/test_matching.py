from domain import local_time, stamp
from matching import evaluate
from conftest import incident_for


def test_positive_match_and_continuity_rank(scenario):
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    eligible = [c for c in candidates if c.eligible]
    assert [c.cleaner_id for c in eligible] == ["C02", "C03"]
    assert eligible[0].continuity
    assert all(len(c.reasons) >= 3 for c in eligible)


def test_region_zone_skill_and_existing_assignment_explained(scenario):
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    by_id = {c.cleaner_id: c for c in candidates}
    assert "Région différente." in by_id["C04"].reasons
    assert "Zone fictive différente." in by_id["C05"].reasons
    assert "Compétence requise absente." in by_id["C06"].reasons
    assert not by_id["C01"].eligible
    assert any("actuellement affecté" in r for r in by_id["C01"].reasons)


def test_conflicting_booking_excluded(scenario):
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    galet = next(c for c in candidates if c.cleaner_id == "C07")
    assert not galet.eligible
    assert any("B007" in r for r in galet.reasons)


def test_full_duration_required_and_no_candidate_has_all_reasons(scenario):
    _, _, candidates = scenario.inspect(incident_for(scenario, "B002"))
    assert len(candidates) == 8
    assert not any(c.eligible for c in candidates)
    assert all(c.reasons for c in candidates)
    assert any("toute la durée" in r for c in candidates if c.cleaner_id == "C06" for r in c.reasons)
    assert any("B008" in r for c in candidates if c.cleaner_id == "C07" for r in c.reasons)


def test_declared_absence_excludes_previously_eligible_cleaner(scenario):
    scenario.simulate_absence("C02", local_time("2026-11-10 09:00"), local_time("2026-11-10 11:00"))
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    c = next(c for c in candidates if c.cleaner_id == "C02")
    assert not c.eligible
    assert any("Indisponibilité" in reason for reason in c.reasons)


def test_stable_id_tie_break_independent_of_input_order(scenario):
    con = scenario.connect()
    try:
        snapshot = scenario._snapshot(con)
    finally:
        con.close()
    snapshot["history"] = set()
    snapshot["bookings"] = [b for b in snapshot["bookings"] if b["id"] != "B014"]
    booking = next(b for b in snapshot["bookings"] if b["id"] == "B001")
    result = evaluate(booking, **snapshot)
    snapshot["cleaners"].reverse()
    result2 = evaluate(booking, **snapshot)
    assert result == result2
    assert [c.cleaner_id for c in result if c.eligible] == ["C02", "C03"]
    assert result[0].day_load == result[1].day_load == 1


def test_lower_day_load_wins_after_equal_continuity(scenario):
    with scenario.transaction() as con:
        con.execute("DELETE FROM history")
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    assert candidates[0].cleaner_id == "C02"  # 1 other booking vs C03's 2.
    assert candidates[0].day_load < candidates[1].day_load


def test_cross_midnight_matching_checks_entire_booking(scenario):
    with scenario.transaction() as con:
        con.execute("UPDATE bookings SET start_at=?,end_at=? WHERE id='B001'",
                    (stamp(local_time("2026-11-10 23:00")), stamp(local_time("2026-11-11 01:00"))))
        con.execute("INSERT INTO shifts(cleaner_id,start_at,end_at) VALUES('C02',?,?)",
                    (stamp(local_time("2026-11-10 22:00")), stamp(local_time("2026-11-11 02:00"))))
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    assert next(c for c in candidates if c.cleaner_id == "C02").eligible
    with scenario.transaction() as con:
        con.execute("INSERT INTO bookings VALUES('B099','F099','Vaud','A','standard',?,?,'C02',0)",
                    (stamp(local_time("2026-11-11 00:30")), stamp(local_time("2026-11-11 01:30"))))
    _, _, candidates = scenario.inspect(incident_for(scenario, "B001"))
    assert not next(c for c in candidates if c.cleaner_id == "C02").eligible
