import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from domain import local_time
from seed import reset_demo
from store import Store


@pytest.fixture
def db(tmp_path):
    db = Store(tmp_path / "demo.sqlite3")
    reset_demo(db)
    return db


@pytest.fixture
def scenario(db):
    db.simulate_absence("C01", local_time("2026-11-10 08:00"), local_time("2026-11-10 17:00"))
    return db


def incident_for(db, booking_id):
    return next(i["id"] for i in db.rows("incidents") if i["booking_id"] == booking_id)


def dataset(db):
    return next(m["value"] for m in db.rows("meta") if m["key"] == "dataset_id")


def approve(db, booking_id="B001", cid="C02", **kwargs):
    return db.approve(incident_for(db, booking_id), cid, 0, "Contrôle humain du scénario.",
                      kwargs.pop("expected_dataset", dataset(db)), **kwargs)
