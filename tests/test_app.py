"""Streamlit's actual script/widget runner; no mock of domain or persistence."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
import seed
from store import Store
from conftest import incident_for

APP = Path(__file__).resolve().parents[1] / "app.py"


def widget(elements, label):
    return next(e for e in elements if e.label == label)


@pytest.fixture
def ui(tmp_path, monkeypatch):
    path = tmp_path / "ui-demo.sqlite3"
    monkeypatch.setattr(seed, "DEFAULT_DB", path)
    app = AppTest.from_file(str(APP), default_timeout=20).run()
    assert not app.exception
    return app, Store(path)


def simulate(app):
    widget(app.button, "Simuler l’absence").click().run()
    assert not app.exception


def test_initial_ui_and_cancellation_manual_review(ui):
    app, db = ui
    assert len(db.rows("incidents")) == 4
    assert any("moins de 48" in w.value for w in app.warning)
    assert widget(app.button, "Annulation automatique indisponible").disabled
    assert "NON ENVOYÉ" in app.text_area[0].value


def test_full_ui_approval_requires_checkbox_then_idempotence(ui):
    app, db = ui
    simulate(app)
    assert len(db.rows("incidents")) == 6
    assert widget(app.button, "Approuver la réaffectation simulée").disabled
    widget(app.button, "Analyser les remplacements").click().run()
    assert not app.exception
    widget(app.button, "Approuver la réaffectation simulée").click().run()
    assert any("Cochez" in e.value for e in app.error)
    assert db.inspect(incident_for(db, "B001"))[1]["cleaner_id"] == "C01"
    app.checkbox[0].set_value(True)
    widget(app.button, "Approuver la réaffectation simulée").click().run()
    assert not app.exception
    assert db.inspect(incident_for(db, "B001"))[1]["cleaner_id"] == "C02"
    assert "NON ENVOYÉ" in app.text_area[0].value
    before = db.rows("audit")
    widget(app.button, "Répéter la même approbation · test d’idempotence").click().run()
    assert db.rows("audit") == before
    assert any("aucune nouvelle" in e.value for e in app.info)


def test_ui_no_match_shows_every_exclusion(ui):
    app, db = ui
    simulate(app)
    widget(app.selectbox, "Prestation à examiner").set_value(incident_for(db, "B002")).run()
    widget(app.button, "Analyser les remplacements").click().run()
    assert not app.exception
    assert any("Aucun candidat admissible" in w.value for w in app.warning)
    assert db.inspect(incident_for(db, "B002"))[0]["status"] == "unresolved"
    assert not any(b.label == "Approuver la réaffectation simulée" for b in app.button)
    markdown = " ".join(m.value for m in app.markdown)
    assert all(cid in markdown for cid in ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08"])


def test_ui_reset_and_all_navigation_views(ui):
    app, db = ui
    simulate(app)
    widget(app.button, "Réinitialiser la démo").click().run()
    assert not app.exception and len(db.rows("incidents")) == 4
    for page in ["Planning & disponibilités", "Journal d’audit", "Mode d’emploi", "File d’intervention"]:
        widget(app.radio, "Navigation").set_value(page).run()
        assert not app.exception


def test_ui_invalid_local_time_keeps_state(ui):
    app, db = ui
    widget(app.text_input, "Début · heure de Zurich").set_value("2026-11-10 18:00")
    widget(app.button, "Simuler l’absence").click().run()
    assert not app.exception
    assert any("fin" in e.value for e in app.error)
    assert len(db.rows("incidents")) == 4
