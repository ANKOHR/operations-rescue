"""SQLite is the only mutation boundary. BEGIN IMMEDIATE serializes approval writers."""
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from domain import REFERENCE_NOW, RuleViolation, instant, overlaps, parse, stamp, window
from matching import evaluate, customer_draft

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS cleaners (
 id TEXT PRIMARY KEY, label TEXT NOT NULL, region TEXT NOT NULL, zone TEXT NOT NULL, skills TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS shifts (
 id INTEGER PRIMARY KEY, cleaner_id TEXT NOT NULL REFERENCES cleaners(id), start_at TEXT NOT NULL, end_at TEXT NOT NULL,
 CHECK(start_at < end_at), UNIQUE(cleaner_id,start_at,end_at));
CREATE TABLE IF NOT EXISTS bookings (
 id TEXT PRIMARY KEY, household_id TEXT NOT NULL, region TEXT NOT NULL, zone TEXT NOT NULL,
 service TEXT NOT NULL, start_at TEXT NOT NULL, end_at TEXT NOT NULL, cleaner_id TEXT NOT NULL REFERENCES cleaners(id),
 version INTEGER NOT NULL DEFAULT 0, CHECK(start_at < end_at));
CREATE TABLE IF NOT EXISTS history (
 household_id TEXT NOT NULL, cleaner_id TEXT NOT NULL REFERENCES cleaners(id), PRIMARY KEY(household_id,cleaner_id));
CREATE TABLE IF NOT EXISTS absences (
 id INTEGER PRIMARY KEY, cleaner_id TEXT NOT NULL REFERENCES cleaners(id), start_at TEXT NOT NULL, end_at TEXT NOT NULL,
 CHECK(start_at < end_at), UNIQUE(cleaner_id,start_at,end_at));
CREATE TABLE IF NOT EXISTS incidents (
 id INTEGER PRIMARY KEY, booking_id TEXT NOT NULL REFERENCES bookings(id),
 kind TEXT NOT NULL CHECK(kind IN ('absence','cancellation')),
 source_cleaner_id TEXT NOT NULL REFERENCES cleaners(id),
 status TEXT NOT NULL CHECK(status IN ('needs_review','candidate_found','approved','unresolved')),
 reason TEXT NOT NULL, created_at TEXT NOT NULL, requested_at TEXT,
 approved_cleaner_id TEXT REFERENCES cleaners(id), approved_at TEXT,
 UNIQUE(booking_id,kind,source_cleaner_id));
CREATE UNIQUE INDEX IF NOT EXISTS one_open_absence ON incidents(booking_id)
 WHERE kind='absence' AND status != 'approved';
CREATE TABLE IF NOT EXISTS audit (
 id INTEGER PRIMARY KEY, event_key TEXT NOT NULL UNIQUE, incident_id INTEGER REFERENCES incidents(id),
 action TEXT NOT NULL, before_json TEXT NOT NULL, after_json TEXT NOT NULL,
 occurred_at TEXT NOT NULL, operator TEXT NOT NULL CHECK(operator='demo_operator'), reason TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS drafts (
 incident_id INTEGER PRIMARY KEY REFERENCES incidents(id), body TEXT NOT NULL,
 state TEXT NOT NULL DEFAULT 'draft_not_sent' CHECK(state='draft_not_sent'));
"""


class Store:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        con = self.connect()
        try:
            con.executescript(SCHEMA)
        finally:
            con.close()

    def connect(self):
        con = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        return con

    @contextmanager
    def transaction(self):
        con = self.connect()
        try:
            con.execute("BEGIN IMMEDIATE")
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def rows(self, table):
        if table not in {"cleaners", "shifts", "bookings", "history", "absences", "incidents", "audit", "drafts", "meta"}:
            raise ValueError("Unknown table")
        con = self.connect()
        try:
            return [dict(r) for r in con.execute(f"SELECT * FROM {table} ORDER BY 1")]
        finally:
            con.close()

    def _snapshot(self, con):
        cleaners = [dict(c) for c in con.execute("SELECT * FROM cleaners ORDER BY id")]
        for c in cleaners:
            c["skills"] = json.loads(c["skills"])
        return dict(cleaners=cleaners,
                    shifts=[dict(r) for r in con.execute("SELECT * FROM shifts")],
                    bookings=[dict(r) for r in con.execute("SELECT * FROM bookings")],
                    absences=[dict(r) for r in con.execute("SELECT * FROM absences")],
                    history={(r[0], r[1]) for r in con.execute("SELECT * FROM history")})

    def _candidates(self, con, incident):
        snapshot = self._snapshot(con)
        booking = next(b for b in snapshot["bookings"] if b["id"] == incident["booking_id"])
        return booking, evaluate(booking, **snapshot)

    def simulate_absence(self, cleaner_id, start, end, now=REFERENCE_NOW):
        start, end = window(start, end)
        if start < instant(now):
            raise RuleViolation("La simulation doit commencer à l’heure de référence ou après.")
        with self.transaction() as con:
            if not con.execute("SELECT 1 FROM cleaners WHERE id=?", (cleaner_id,)).fetchone():
                raise RuleViolation("Intervenant inconnu.")
            cursor = con.execute("INSERT OR IGNORE INTO absences(cleaner_id,start_at,end_at) VALUES(?,?,?)",
                                 (cleaner_id, stamp(start), stamp(end)))
            if cursor.rowcount:
                self._audit(con, f"absence:{cursor.lastrowid}", None, "absence_declared", {},
                            {"cleaner_id": cleaner_id, "start_at": stamp(start), "end_at": stamp(end)}, now,
                            "Indisponibilité fictive déclarée par un opérateur.")
            created = []
            for booking in con.execute("SELECT * FROM bookings WHERE cleaner_id=? ORDER BY start_at,id", (cleaner_id,)).fetchall():
                if parse(booking["start_at"]) < instant(now):
                    continue
                if overlaps(start, end, parse(booking["start_at"]), parse(booking["end_at"])):
                    cur = con.execute("""INSERT OR IGNORE INTO incidents
                        (booking_id,kind,source_cleaner_id,status,reason,created_at)
                        VALUES(?,'absence',?,'needs_review',?,?)""",
                        (booking["id"], cleaner_id, "Intervenant indisponible sur le créneau réservé.", stamp(now)))
                    if cur.rowcount:
                        created.append(cur.lastrowid)
            return created

    def inspect(self, incident_id):
        con = self.connect()
        try:
            con.execute("BEGIN")
            incident = con.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
            if not incident:
                raise RuleViolation("Incident inconnu.")
            booking, candidates = self._candidates(con, incident)
            return dict(incident), booking, candidates
        finally:
            con.rollback()
            con.close()

    def analyze(self, incident_id):
        with self.transaction() as con:
            incident = con.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
            if not incident or incident["kind"] != "absence":
                raise RuleViolation("Cette demande nécessite une revue humaine.")
            _, candidates = self._candidates(con, incident)
            if incident["status"] != "approved":
                status = "candidate_found" if any(c.eligible for c in candidates) else "unresolved"
                con.execute("UPDATE incidents SET status=? WHERE id=?", (status, incident_id))
            return candidates

    @staticmethod
    def _audit(con, key, incident_id, action, before, after, now, reason):
        con.execute("""INSERT INTO audit(event_key,incident_id,action,before_json,after_json,occurred_at,operator,reason)
            VALUES(?,?,?,?,?,?,'demo_operator',?)""",
            (key, incident_id, action, json.dumps(before, sort_keys=True, ensure_ascii=False),
             json.dumps(after, sort_keys=True, ensure_ascii=False), stamp(now), reason))

    def approve(self, incident_id, cleaner_id, expected_version, reason, expected_dataset, now=REFERENCE_NOW):
        if not reason or not reason.strip():
            raise RuleViolation("Un motif opérateur est obligatoire.")
        with self.transaction() as con:
            dataset = con.execute("SELECT value FROM meta WHERE key='dataset_id'").fetchone()
            if not dataset or dataset[0] != expected_dataset:
                raise RuleViolation("La démonstration a été réinitialisée. Rechargez le dossier.")
            incident = con.execute("SELECT * FROM incidents WHERE id=?", (incident_id,)).fetchone()
            if not incident or incident["kind"] != "absence":
                raise RuleViolation("Annulation ou incident inconnu : décision humaine obligatoire.")
            if incident["status"] == "approved":
                if incident["approved_cleaner_id"] != cleaner_id:
                    raise RuleViolation("Incident déjà approuvé avec un autre intervenant.")
                return {"result": "already_approved", "incident_id": incident_id}
            booking, candidates = self._candidates(con, incident)
            if parse(booking["start_at"]) <= instant(now):
                raise RuleViolation("Prestation commencée ou passée : revue humaine requise.")
            if booking["version"] != expected_version or booking["cleaner_id"] != incident["source_cleaner_id"]:
                raise RuleViolation("Affectation modifiée depuis l’analyse. Actualisez le dossier.")
            candidate = next((c for c in candidates if c.cleaner_id == cleaner_id), None)
            if not candidate or not candidate.eligible:
                detail = " ".join(candidate.reasons) if candidate else "Intervenant inconnu."
                raise RuleViolation("Approbation refusée après recontrôle : " + detail)
            con.execute("UPDATE bookings SET cleaner_id=?,version=version+1 WHERE id=?", (cleaner_id, booking["id"]))
            con.execute("UPDATE incidents SET status='approved',approved_cleaner_id=?,approved_at=? WHERE id=?",
                        (cleaner_id, stamp(now), incident_id))
            self._audit(con, f"approval:{incident_id}", incident_id, "reassignment_approved",
                        {"cleaner_id": booking["cleaner_id"], "version": booking["version"], "booking_id": booking["id"]},
                        {"cleaner_id": cleaner_id, "version": booking["version"] + 1, "booking_id": booking["id"]}, now, reason.strip())
            draft = customer_draft(booking, approved=True, cleaner_label=candidate.label)
            con.execute("INSERT INTO drafts(incident_id,body) VALUES(?,?)", (incident_id, draft))
            return {"result": "approved", "incident_id": incident_id}

    def draft(self, incident_id):
        saved = next((r["body"] for r in self.rows("drafts") if r["incident_id"] == incident_id), None)
        if saved:
            return saved
        incident, booking, _ = self.inspect(incident_id)
        if incident["kind"] == "cancellation":
            return ("BROUILLON, NON ENVOYÉ — validation du texte requise\n\nBonjour,\n\n"
                    "Votre demande d’annulation est en cours d’examen par notre équipe. "
                    "Aucune décision sur les frais ou le remboursement n’est confirmée.\n\n"
                    "L’équipe — démonstration fictive")
        return customer_draft(booking)
