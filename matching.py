"""No AI endpoint or travel inference: every exclusion and ranking is explainable."""
from datetime import datetime, time, timedelta
from domain import Candidate, ZURICH, overlaps, parse, window


def evaluate(booking, cleaners, shifts, bookings, absences, history):
    start, end = window(parse(booking["start_at"]), parse(booking["end_at"]))
    day = start.astimezone(ZURICH).date()
    results = []
    for cleaner in cleaners:
        cid = cleaner["id"]
        failures = []
        if cid == booking["cleaner_id"]:
            failures.append("Intervenant actuellement affecté à cette prestation.")
        if cleaner["region"] != booking["region"]:
            failures.append("Région différente.")
        if cleaner["zone"] != booking["zone"]:
            failures.append("Zone fictive différente.")
        if booking["service"] not in cleaner["skills"]:
            failures.append("Compétence requise absente.")
        if not any(s["cleaner_id"] == cid and parse(s["start_at"]) <= start
                   and end <= parse(s["end_at"]) for s in shifts):
            failures.append("Plage de travail ne couvrant pas toute la durée.")
        if any(a["cleaner_id"] == cid and overlaps(start, end, parse(a["start_at"]), parse(a["end_at"]))
               for a in absences):
            failures.append("Indisponibilité déclarée sur ce créneau.")
        conflicts = [b["id"] for b in bookings if b["id"] != booking["id"] and b["cleaner_id"] == cid
                     and overlaps(start, end, parse(b["start_at"]), parse(b["end_at"]))]
        if conflicts:
            failures.append("Conflit avec " + ", ".join(sorted(conflicts)) + ".")
        # Count every assignment intersecting the Zurich calendar day, including overnight ones.
        day_start = datetime.combine(day, time.min, tzinfo=ZURICH)
        day_end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=ZURICH)
        load = sum(b["cleaner_id"] == cid and b["id"] != booking["id"]
                   and overlaps(day_start, day_end, parse(b["start_at"]), parse(b["end_at"]))
                   for b in bookings)
        continuity = (booking["household_id"], cid) in history
        reasons = tuple(failures) if failures else (
            "Région, zone et compétence compatibles.",
            "Durée entièrement couverte ; aucun conflit ni absence.",
            "Déjà intervenu pour ce foyer fictif." if continuity else "Pas de continuité connue pour ce foyer fictif.",
            f"Autres prestations ce jour : {load}.",
        )
        results.append(Candidate(cid, cleaner["label"], not failures, reasons, continuity, load))
    return sorted(results, key=lambda c: (not c.eligible, c.rank_key))


def customer_draft(booking, approved=False, cleaner_label=None):
    from domain import display
    when = display(booking["start_at"])
    header = "BROUILLON, NON ENVOYÉ — validation du texte requise\n\n"
    if approved:
        return (header + f"Bonjour,\n\nUn remplacement pour votre prestation du {when} a été validé "
                f"dans notre simulation locale ({cleaner_label}). Notre équipe reste à votre disposition "
                "pour examiner cette proposition avec vous.\n\nMerci,\nL’équipe — démonstration fictive")
    return (header + f"Bonjour,\n\nNotre équipe examine une possibilité de remplacement pour votre prestation "
            f"du {when}. Aucune modification n’est confirmée à ce stade. "
            "Nous reviendrons vers vous après vérification humaine.\n\nMerci,\nL’équipe — démonstration fictive")
