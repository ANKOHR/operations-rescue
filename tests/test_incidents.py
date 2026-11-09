from concurrent.futures import ThreadPoolExecutor
import json
import sqlite3
import pytest
from domain import RuleViolation, local_time, stamp
from seed import reset_demo
from store import Store
from conftest import approve, dataset, incident_for


def test_seed_counts_and_no_existing_double_assignments(db):
    from domain import overlaps, parse
    assert len(db.rows("cleaners")) == 8
    assert len(db.rows("bookings")) == 18
    assert len(db.rows("incidents")) == 4
    for a in db.rows("bookings"):
        for b in db.rows("bookings"):
            if a["id"] < b["id"] and a["cleaner_id"] == b["cleaner_id"]:
                assert not overlaps(parse(a["start_at"]), parse(a["end_at"]), parse(b["start_at"]), parse(b["end_at"]))


def test_simulation_creates_two_incidents_without_duplicates(db):
    a, b = local_time("2026-11-10 08:00"), local_time("2026-11-10 17:00")
    assert len(db.simulate_absence("C01", a, b)) == 2
    assert db.simulate_absence("C01", a, b) == []
    assert db.simulate_absence("C01", local_time("2026-11-10 08:30"), b) == []
    assert len(db.rows("incidents")) == 6


def test_invalid_and_past_absences_leave_database_unchanged(db):
    before = db.rows("absences")
    with pytest.raises(RuleViolation):
        db.simulate_absence("UNKNOWN", local_time("2026-11-10 08:00"), local_time("2026-11-10 17:00"))
    with pytest.raises(RuleViolation):
        db.simulate_absence("C01", local_time("2026-11-08 08:00"), local_time("2026-11-10 17:00"))
    assert db.rows("absences") == before


def test_analyze_changes_only_incident_state_and_never_assigns(scenario):
    before = scenario.rows("bookings")
    scenario.analyze(incident_for(scenario, "B001"))
    scenario.analyze(incident_for(scenario, "B002"))
    assert scenario.inspect(incident_for(scenario, "B001"))[0]["status"] == "candidate_found"
    assert scenario.inspect(incident_for(scenario, "B002"))[0]["status"] == "unresolved"
    assert scenario.rows("bookings") == before
    assert not scenario.rows("drafts")


def test_approval_persists_audit_before_after_and_single_unsent_draft(scenario):
    assert approve(scenario)["result"] == "approved"
    incident, booking, _ = scenario.inspect(incident_for(scenario, "B001"))
    assert booking["cleaner_id"] == "C02" and booking["version"] == 1
    assert incident["status"] == "approved"
    event = next(a for a in scenario.rows("audit") if a["action"] == "reassignment_approved")
    assert json.loads(event["before_json"])["cleaner_id"] == "C01"
    assert json.loads(event["after_json"])["cleaner_id"] == "C02"
    assert event["operator"] == "demo_operator"
    assert event["occurred_at"] == "2026-11-09T07:00:00+00:00"
    assert event["reason"] == "Contrôle humain du scénario."
    draft = scenario.rows("drafts")[0]
    assert draft["state"] == "draft_not_sent"
    assert "NON ENVOYÉ" in draft["body"]


def test_repeated_approval_is_idempotent_and_different_choice_refused(scenario):
    approve(scenario)
    before = {t: scenario.rows(t) for t in ("bookings", "incidents", "audit", "drafts")}
    assert approve(scenario)["result"] == "already_approved"
    with pytest.raises(RuleViolation, match="déjà approuvé"):
        approve(scenario, cid="C03")
    assert before == {t: scenario.rows(t) for t in before}


def test_approval_rechecks_conflict_added_after_analysis(scenario):
    scenario.analyze(incident_for(scenario, "B001"))
    with scenario.transaction() as con:
        con.execute("INSERT INTO bookings VALUES('B099','F099','Vaud','A','standard',?,?,'C02',0)",
                    (stamp(local_time("2026-11-10 10:00")), stamp(local_time("2026-11-10 12:00"))))
    before = scenario.rows("audit")
    with pytest.raises(RuleViolation, match="B099"):
        approve(scenario)
    assert scenario.inspect(incident_for(scenario, "B001"))[1]["cleaner_id"] == "C01"
    assert scenario.rows("audit") == before
    assert not scenario.rows("drafts")


def test_approval_rechecks_new_absence(scenario):
    scenario.analyze(incident_for(scenario, "B001"))
    scenario.simulate_absence("C02", local_time("2026-11-10 09:00"), local_time("2026-11-10 11:00"))
    with pytest.raises(RuleViolation, match="Indisponibilité"):
        approve(scenario)


def test_stale_booking_version_refused(scenario):
    with scenario.transaction() as con:
        con.execute("UPDATE bookings SET version=1 WHERE id='B001'")
    with pytest.raises(RuleViolation, match="modifiée"):
        approve(scenario)


def test_started_booking_refused(scenario):
    with pytest.raises(RuleViolation, match="commencée"):
        approve(scenario, now=local_time("2026-11-10 09:00"))


def test_cancellation_cannot_be_approved_or_analyzed_as_reassignment(scenario):
    before = scenario.rows("bookings")
    with pytest.raises(RuleViolation, match="humaine"):
        approve(scenario, "B014")
    with pytest.raises(RuleViolation, match="humaine"):
        scenario.analyze(incident_for(scenario, "B014"))
    assert scenario.rows("bookings") == before


def test_no_safe_match_refuses_forced_assignment(scenario):
    with pytest.raises(RuleViolation, match="refusée"):
        approve(scenario, "B002", cid="C06")
    assert scenario.inspect(incident_for(scenario, "B002"))[1]["cleaner_id"] == "C01"


def test_empty_operator_reason_refused(scenario):
    with pytest.raises(RuleViolation, match="motif"):
        scenario.approve(incident_for(scenario, "B001"), "C02", 0, " ", dataset(scenario))


def test_failure_while_saving_draft_rolls_back_assignment_and_audit(scenario):
    with scenario.transaction() as con:
        con.execute("""CREATE TRIGGER fail_draft BEFORE INSERT ON drafts BEGIN
            SELECT RAISE(ABORT,'injected disk/write failure'); END""")
    before = {t: scenario.rows(t) for t in ("bookings", "incidents", "audit", "drafts")}
    with pytest.raises(sqlite3.IntegrityError, match="injected"):
        approve(scenario)
    assert before == {t: scenario.rows(t) for t in before}


def test_two_concurrent_approvals_cannot_double_book_candidate(scenario):
    with scenario.transaction() as con:
        con.execute("INSERT INTO bookings VALUES('B019','F019','Vaud','A','standard',?,?,'C01',0)",
                    (stamp(local_time("2026-11-10 09:00")), stamp(local_time("2026-11-10 10:00"))))
    scenario.simulate_absence("C01", local_time("2026-11-10 08:00"), local_time("2026-11-10 17:00"))
    token = dataset(scenario)
    def attempt(bid):
        try:
            return approve(Store(scenario.path), bid, expected_dataset=token)["result"]
        except RuleViolation:
            return "refused"
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(attempt, ["B001", "B019"]))
    assert sorted(results) == ["approved", "refused"]
    assert len([a for a in scenario.rows("audit") if a["action"] == "reassignment_approved"]) == 1


def test_reset_restores_dataset_and_rejects_old_review_token(scenario):
    token = dataset(scenario)
    original = scenario.rows("bookings")
    approve(scenario)
    reset_demo(scenario)
    assert scenario.rows("bookings") == original
    assert len(scenario.rows("incidents")) == 4
    assert dataset(scenario) != token
    scenario.simulate_absence("C01", local_time("2026-11-10 08:00"), local_time("2026-11-10 17:00"))
    with pytest.raises(RuleViolation, match="réinitialisée"):
        approve(scenario, expected_dataset=token)


def test_reset_refuses_unmarked_database(db):
    with db.transaction() as con:
        con.execute("DELETE FROM meta")
    before = db.rows("bookings")
    with pytest.raises(RuleViolation, match="non identifiée"):
        reset_demo(db)
    assert db.rows("bookings") == before


def test_draft_before_approval_never_claims_confirmation(scenario):
    text = scenario.draft(incident_for(scenario, "B001"))
    assert "NON ENVOYÉ" in text and "Aucune modification n’est confirmée" in text
    assert scenario.rows("drafts") == []
