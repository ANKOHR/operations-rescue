"""One deterministic fictional dataset. Reset is atomic and restricted to demo-owned data."""
import argparse
import json
import uuid
from pathlib import Path
from domain import REFERENCE_NOW, RuleViolation, local_time, stamp
from store import Store

DEFAULT_DB = Path(__file__).resolve().parent / "data" / "demo.sqlite3"


def reset_demo(store):
    with store.transaction() as con:
        owned = con.execute("SELECT value FROM meta WHERE key='demo_owned'").fetchone()
        if not owned and any(con.execute(f"SELECT 1 FROM {t} LIMIT 1").fetchone()
                             for t in ("cleaners", "bookings", "incidents", "audit")):
            raise RuleViolation("Réinitialisation refusée : base non identifiée comme démonstration.")
        if owned and owned[0] != "operations-rescue-synthetic-v1":
            raise RuleViolation("Réinitialisation refusée : marqueur de démonstration inconnu.")
        for table in ("drafts", "audit", "incidents", "absences", "history", "bookings", "shifts", "cleaners", "meta"):
            con.execute(f"DELETE FROM {table}")
        con.executemany("INSERT INTO meta(key,value) VALUES(?,?)", [
            ("demo_owned", "operations-rescue-synthetic-v1"),
            ("dataset_id", str(uuid.uuid4())),  # Only concurrency token varies; sample records do not.
            ("reference_now", stamp(REFERENCE_NOW)), ("seed_version", "1")])
        cleaners = [
            ("C01", "Agent Aster · fictif", "Vaud", "A", ["standard", "vitres"]),
            ("C02", "Agent Brume · fictif", "Vaud", "A", ["standard"]),
            ("C03", "Agent Cobalt · fictif", "Vaud", "A", ["standard"]),
            ("C04", "Agent Dune · fictif", "Genève", "A", ["standard"]),
            ("C05", "Agent Éclat · fictif", "Vaud", "B", ["standard", "vitres"]),
            ("C06", "Agent Flocon · fictif", "Vaud", "A", ["vitres"]),
            ("C07", "Agent Galet · fictif", "Vaud", "A", ["standard", "vitres"]),
            ("C08", "Agent Halo · fictif", "Fribourg", "C", ["standard"]),
        ]
        con.executemany("INSERT INTO cleaners VALUES(?,?,?,?,?)",
                        [(a, b, c, d, json.dumps(e)) for a, b, c, d, e in cleaners])
        for cid, *_ in cleaners:
            for day in range(9, 14):
                # A partial shift is deliberate: Flocon cannot cover B002's afternoon window.
                shift_end = "12:00" if cid == "C06" else "18:00"
                con.execute("INSERT INTO shifts(cleaner_id,start_at,end_at) VALUES(?,?,?)",
                            (cid, stamp(local_time(f"2026-11-{day:02} 08:00")),
                             stamp(local_time(f"2026-11-{day:02} {shift_end}"))))
        # Locations are just region + invented zone; there are no real addresses or customers.
        specs = [
            ("B001", "F001", "C01", 10, "09:00", "11:00", "standard"),
            ("B002", "F002", "C01", 10, "13:00", "16:00", "vitres"),
            ("B003", "F003", "C02", 10, "13:00", "15:00", "standard"),
            ("B004", "F004", "C03", 10, "11:00", "13:00", "standard"),
            ("B005", "F005", "C04", 10, "09:00", "11:00", "standard"),
            ("B006", "F006", "C05", 10, "09:00", "11:00", "vitres"),
            ("B007", "F007", "C07", 10, "09:00", "11:00", "standard"),
            ("B008", "F008", "C07", 10, "13:00", "17:00", "vitres"),
            ("B009", "F009", "C08", 10, "09:00", "11:00", "standard"),
            ("B010", "F010", "C01", 11, "09:00", "11:00", "standard"),
            ("B011", "F011", "C04", 11, "09:00", "11:00", "standard"),
            ("B012", "F012", "C05", 11, "13:00", "15:00", "standard"),
            ("B013", "F013", "C08", 12, "09:00", "11:00", "standard"),
            ("B014", "F014", "C03", 10, "08:00", "09:00", "standard"),
            ("B015", "F015", "C02", 11, "13:00", "15:00", "standard"),
            ("B016", "F016", "C06", 11, "09:00", "11:00", "vitres"),
            ("B017", "F017", "C07", 12, "13:00", "15:00", "standard"),
            ("B018", "F018", "C01", 13, "09:00", "11:00", "standard"),
        ]
        geography = {c[0]: (c[2], c[3]) for c in cleaners}
        for bid, home, cid, day, start, end, service in specs:
            region, zone = geography[cid]
            con.execute("""INSERT INTO bookings
                (id,household_id,region,zone,service,start_at,end_at,cleaner_id) VALUES(?,?,?,?,?,?,?,?)""",
                (bid, home, region, zone, service, stamp(local_time(f"2026-11-{day:02} {start}")),
                 stamp(local_time(f"2026-11-{day:02} {end}")), cid))
        con.execute("INSERT INTO history VALUES('F001','C02')")
        for cid, bid, day, start, end in [
            ("C04", "B011", 11, "08:00", "12:00"),
            ("C05", "B012", 11, "12:00", "18:00"),
            ("C08", "B013", 12, "08:00", "12:00")]:
            a, b = stamp(local_time(f"2026-11-{day:02} {start}")), stamp(local_time(f"2026-11-{day:02} {end}"))
            cur = con.execute("INSERT INTO absences(cleaner_id,start_at,end_at) VALUES(?,?,?)", (cid, a, b))
            store._audit(con, f"absence:{cur.lastrowid}", None, "absence_declared", {},
                         {"cleaner_id": cid, "start_at": a, "end_at": b}, REFERENCE_NOW, "Incident fictif préchargé.")
            con.execute("""INSERT INTO incidents(booking_id,kind,source_cleaner_id,status,reason,created_at)
                VALUES(?,'absence',?,'needs_review',?,?)""",
                (bid, cid, "Absence fictive préchargée ; prestation à réexaminer.", stamp(REFERENCE_NOW)))
        con.execute("""INSERT INTO incidents(booking_id,kind,source_cleaner_id,status,reason,created_at,requested_at)
            VALUES('B014','cancellation','C03','needs_review',?,?,?)""",
            ("Demande fictive à 24 h du passage : décision opérateur requise, aucun frais calculé.",
             stamp(REFERENCE_NOW), stamp(REFERENCE_NOW)))


def initialize(store):
    if not store.rows("meta"):
        reset_demo(store)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the bundled synthetic demo database only.")
    parser.add_argument("--reset-demo", action="store_true", help="Replace this app’s demo dataset")
    args = parser.parse_args()
    db = Store(DEFAULT_DB)
    if args.reset_demo:
        reset_demo(db)
        print(f"Synthetic demo reset: {DEFAULT_DB}")
    else:
        initialize(db)
        print(f"Synthetic demo ready: {DEFAULT_DB}")
