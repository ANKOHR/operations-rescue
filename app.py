"""French local decision-support UI. All writes route through Store's transaction boundary."""
import json
import streamlit as st

from domain import RuleViolation, cancellation_review, display, local_time, parse
from seed import DEFAULT_DB, initialize, reset_demo
from store import Store

st.set_page_config(page_title="Operations Rescue · MénageSimple", page_icon="◈", layout="wide")
st.markdown("""<style>
.block-container {max-width:1380px; padding-top:4rem; padding-bottom:3rem;}
h1 {font-size:2.3rem !important; letter-spacing:-.07rem; font-weight:700 !important;}
h2 {font-size:1.45rem !important; letter-spacing:-.025rem;}
h3 {font-size:1.1rem !important;}
[data-testid="stSidebar"] {border-right:1px solid #DFE7E9;}
[data-testid="stMetric"] {background:white; border:1px solid #DFE7E9; border-radius:12px; padding:1rem 1.2rem;}
[data-testid="stMetricValue"] {font-size:1.9rem;}
.eyebrow {color:#087F75; font-size:.75rem; font-weight:700; letter-spacing:.13rem; margin-bottom:.6rem;}
.brand {font-size:1.4rem; font-weight:750; letter-spacing:-.04rem; color:#182E38;}
.brand span {color:#087F75;}
.brand-sub {font-size:.8rem; color:#5B6E77; margin:.2rem 0 1.7rem;}
.notice {background:#E7F3F0; border:1px solid #CAE2DC; border-radius:10px; padding:.7rem 1rem; color:#21574D; font-size:.86rem; margin:1rem 0 1.4rem;}
.step {color:#5B6E77; font-size:.8rem; margin-bottom:.6rem;}
[data-testid="stVerticalBlockBorderWrapper"] {border-radius:12px;}
textarea:disabled {color:#40545E !important; -webkit-text-fill-color:#40545E !important; opacity:1 !important;}
@media(max-width:700px) {h1{font-size:1.8rem !important;} .block-container{padding:1rem;}}
</style>""", unsafe_allow_html=True)

db = Store(DEFAULT_DB)
initialize(db)
metadata = {r["key"]: r["value"] for r in db.rows("meta")}
dataset_id = metadata["dataset_id"]
if st.session_state.get("dataset_id") != dataset_id:
    for key in ("dossier_id", "review_snapshot", "candidate_choice", "human_checked"):
        st.session_state.pop(key, None)
    st.session_state.dataset_id = dataset_id

LABELS = {"needs_review": "À examiner", "candidate_found": "Candidat trouvé",
          "approved": "Approuvé", "unresolved": "Sans solution"}
COLORS = {"needs_review": "orange", "candidate_found": "blue", "approved": "green", "unresolved": "red"}
names = {c["id"]: c["label"] for c in db.rows("cleaners")}

with st.sidebar:
    st.markdown('<div class="brand"><span>◈</span> Operations Rescue</div><div class="brand-sub">Étude de cas · MénageSimple</div>', unsafe_allow_html=True)
    page = st.radio("Navigation", ["File d’intervention", "Planning & disponibilités", "Journal d’audit", "Mode d’emploi"], label_visibility="collapsed")
    st.divider()
    st.caption("HORLOGE DE DÉMONSTRATION")
    st.markdown("**Lundi 9 novembre 2026 · 08:00**")
    st.caption("Europe/Zurich · référence fixe")
    with st.expander("Simuler une absence", expanded=True):
        st.caption("Scénario conseillé : C01 · 10 novembre, 08:00–17:00. Deux prestations touchées.")
        with st.form("absence_form"):
            cid = st.selectbox("Intervenant fictif", list(names), format_func=lambda c: f"{c} · {names[c]}")
            start_text = st.text_input("Début · heure de Zurich", "2026-11-10 08:00")
            end_text = st.text_input("Fin · heure de Zurich", "2026-11-10 17:00")
            absence_submit = st.form_submit_button("Simuler l’absence", type="primary", width="stretch")
        if absence_submit:
            try:
                created = db.simulate_absence(cid, local_time(start_text), local_time(end_text))
                if created:
                    st.session_state.dossier_id = created[0]
                    st.session_state.pop("review_snapshot", None)
                st.session_state.flash = ("success", f"{len(created)} nouveau(x) dossier(s). Les répétitions ne créent pas de doublons.")
                st.rerun()
            except (RuleViolation, ValueError) as exc:
                st.error(str(exc))
    with st.expander("Outils de démonstration"):
        st.caption("Restaure les 18 prestations fictives et les 4 dossiers initiaux. Efface uniquement l’état de cette démo.")
        if st.button("Réinitialiser la démo", width="stretch"):
            reset_demo(db)
            st.session_state.flash = ("success", "Jeu fictif restauré. Nouvelle session de démonstration.")
            st.rerun()
    st.caption("100 % fictif · local · aucun envoi")

st.markdown('<div class="eyebrow">DÉCISION ASSISTÉE · VALIDATION HUMAINE</div>', unsafe_allow_html=True)
st.title({"File d’intervention": "Remplacements à examiner", "Planning & disponibilités": "Un planning lisible, avant de décider",
          "Journal d’audit": "Chaque décision laisse une trace", "Mode d’emploi": "Une démo courte, des limites explicites"}[page])
st.markdown('<div class="notice">Prototype indépendant · données entièrement synthétiques · aucune connexion aux systèmes MénageSimple · aucun message envoyé</div>', unsafe_allow_html=True)
if "flash" in st.session_state:
    level, message = st.session_state.pop("flash")
    getattr(st, level)(message)

incidents = db.rows("incidents")
bookings = {b["id"]: b for b in db.rows("bookings")}


def queue_rows():
    return [{"Dossier": f"D{i['id']:03}", "Prestation": i["booking_id"],
             "Type": "Absence" if i["kind"] == "absence" else "Annulation · revue humaine",
             "Début · Zurich": display(bookings[i["booking_id"]]["start_at"]),
             "Secteur fictif": bookings[i["booking_id"]]["region"] + " · " + bookings[i["booking_id"]]["zone"],
             "État": LABELS[i["status"]]} for i in sorted(incidents, key=lambda i: (bookings[i["booking_id"]]["start_at"], i["id"]))]


if page == "File d’intervention":
    st.write("Repérer la perturbation, examiner les alternatives, puis approuver une réaffectation locale.")
    a, b, c, d = st.columns(4)
    a.metric("À examiner", sum(i["status"] == "needs_review" for i in incidents))
    b.metric("Candidat trouvé", sum(i["status"] == "candidate_found" for i in incidents))
    c.metric("Approuvés", sum(i["status"] == "approved" for i in incidents))
    d.metric("Sans solution", sum(i["status"] == "unresolved" for i in incidents))
    st.caption("Comptages du jeu de démonstration ; aucune mesure de gains réels.")
    with st.expander(f"File complète · {len(incidents)} dossiers", expanded=False):
        st.dataframe(queue_rows(), hide_index=True, width="stretch")
    st.markdown("### 1 · Choisir un dossier")
    options = [i["id"] for i in sorted(incidents, key=lambda i: (bookings[i["booking_id"]]["start_at"], i["id"]))]
    by_id = {i["id"]: i for i in incidents}
    def dossier_label(i):
        item = by_id[i]
        bk = bookings[item["booking_id"]]
        # Keep option labels stable: status changes must not reset the browser selection.
        return f"{item['booking_id']} · {bk['region']} {bk['zone']} · {display(bk['start_at'])}"
    selected = st.selectbox("Prestation à examiner", options, format_func=dossier_label, key="dossier_id")
    incident, booking, candidates = db.inspect(selected)
    with st.container(border=True):
        left, right = st.columns([3, 1])
        with left:
            st.markdown(f"**{booking['id']} · Foyer fictif {booking['household_id']}**")
            st.write(f"{display(booking['start_at'])} → {display(booking['end_at'])}")
            st.caption(f"{booking['region']} · zone fictive {booking['zone']} · {booking['service']} · affectation : {booking['cleaner_id']}")
        with right:
            st.badge(LABELS[incident["status"]], color=COLORS[incident["status"]])
        st.caption(f"Intervenant au moment du signalement : {incident['source_cleaner_id']}")
        st.write(incident["reason"])
    if incident["kind"] == "cancellation":
        late = cancellation_review(parse(booking["start_at"]), parse(incident["requested_at"]))
        st.warning("Demande à moins de 48 heures : revue humaine obligatoire." if late else "Demande à 48 heures ou plus : examen humain conservé.")
        st.write("Ce prototype refuse d’annuler automatiquement. Il ne calcule ni frais ni remboursement et conserve l’affectation.")
        st.button("Annulation automatique indisponible", disabled=True)
        st.markdown("### Brouillon client · non envoyé")
        st.text_area("À relire manuellement", db.draft(selected), height=210, disabled=True, key=f"cancel_draft_{selected}")
    elif incident["status"] == "approved":
        st.success(f"Réaffectation simulée approuvée : {incident['source_cleaner_id']} → {incident['approved_cleaner_id']}.")
        st.caption("L’approbation et le brouillon ont été enregistrés dans une seule transaction locale.")
        if st.button("Répéter la même approbation · test d’idempotence"):
            try:
                result = db.approve(selected, incident["approved_cleaner_id"], booking["version"],
                                    "Répétition de démonstration.", dataset_id)
                st.info("Déjà approuvé : aucune nouvelle affectation, aucun nouvel événement ni brouillon.")
            except RuleViolation as exc:
                st.error(str(exc))
        st.markdown("### Brouillon client · non envoyé")
        st.text_area("À relire manuellement", db.draft(selected), height=230, disabled=True, key=f"approved_draft_{selected}")
        st.caption("Voir le journal pour les valeurs avant/après, le motif et l’opérateur.")
    else:
        st.markdown("### 2 · Examiner les remplacements")
        st.caption("Ordre stable : continuité du foyer → moins d’autres prestations ce jour → identifiant. Les règles précèdent le classement.")
        if st.button("Analyser les remplacements", type="primary"):
            db.analyze(selected)
            st.session_state.review_snapshot = {"incident_id": selected, "version": booking["version"], "dataset_id": dataset_id}
            st.rerun()
        review = st.session_state.get("review_snapshot", {})
        reviewed = review.get("incident_id") == selected and review.get("dataset_id") == dataset_id
        eligible = [candidate for candidate in candidates if candidate.eligible]
        if not reviewed:
            st.info("Aperçu des règles ci-dessous. Lancez l’analyse avant toute approbation.")
        if eligible:
            for rank, candidate in enumerate(eligible, 1):
                with st.container(border=True):
                    st.markdown(f"**{rank:02} · {candidate.cleaner_id} · {candidate.label}**")
                    if candidate.continuity:
                        st.badge("Continuité du foyer", color="green")
                    st.write(" ".join(candidate.reasons))
        else:
            st.warning("Aucun candidat admissible selon les règles de la démo. Intervention humaine requise ; aucune affectation forcée.")
        excluded = [candidate for candidate in candidates if not candidate.eligible]
        with st.expander(f"Comprendre les exclusions · {len(excluded)} intervenants", expanded=not eligible):
            for candidate in excluded:
                st.markdown(f"**{candidate.cleaner_id} · {candidate.label}**")
                for reason in candidate.reasons:
                    st.write("• " + reason)
        if eligible:
            st.markdown("### 3 · Valider une décision locale")
            st.caption("Les déplacements, l’accord du foyer et celui de l’intervenant restent à vérifier par une personne. Aucun temps de trajet n’est estimé.")
            with st.form(f"approval_{selected}"):
                choice = st.selectbox("Candidat retenu", [candidate.cleaner_id for candidate in eligible],
                                      format_func=lambda cid: f"{cid} · {names[cid]}")
                reason = st.text_input("Motif de la décision", "Compatibilité et continuité examinées dans ce scénario fictif.")
                checked = st.checkbox("J’ai examiné les limites et je valide cette réaffectation fictive.")
                submit = st.form_submit_button("Approuver la réaffectation simulée", type="primary", disabled=not reviewed)
            if submit:
                try:
                    if not checked:
                        raise RuleViolation("Cochez la validation humaine avant d’approuver.")
                    db.approve(selected, choice, review["version"], reason, review["dataset_id"])
                    st.session_state.flash = ("success", "Réaffectation locale approuvée. Journal et brouillon enregistrés ; rien n’a été envoyé.")
                    st.rerun()
                except RuleViolation as exc:
                    st.error(str(exc))
            with st.expander("Aperçu du brouillon avant décision · non envoyé"):
                st.text(db.draft(selected))

elif page == "Planning & disponibilités":
    st.write("18 prestations et 8 intervenants inventés. Les zones A, B et C ne représentent aucun découpage réel.")
    booking_tab, cleaner_tab, absence_tab = st.tabs(["Prestations", "Intervenants & plages", "Indisponibilités"])
    with booking_tab:
        region = st.selectbox("Filtrer par région", ["Toutes"] + sorted({b["region"] for b in bookings.values()}))
        st.dataframe([{"Prestation": b["id"], "Foyer fictif": b["household_id"], "Secteur": b["region"] + " · " + b["zone"],
                       "Service": b["service"], "Début · Zurich": display(b["start_at"]), "Fin · Zurich": display(b["end_at"]),
                       "Intervenant": b["cleaner_id"], "Version": b["version"]}
                      for b in sorted(bookings.values(), key=lambda b: (b["start_at"], b["id"]))
                      if region == "Toutes" or b["region"] == region], hide_index=True, width="stretch")
    with cleaner_tab:
        st.dataframe([{"ID": c["id"], "Nom fictif": c["label"], "Région": c["region"], "Zone fictive": c["zone"],
                       "Compétences": ", ".join(json.loads(c["skills"]))} for c in db.rows("cleaners")], hide_index=True, width="stretch")
        st.markdown("#### Plages de travail déclarées")
        st.dataframe([{"Intervenant": s["cleaner_id"], "Début": display(s["start_at"]), "Fin": display(s["end_at"])}
                      for s in db.rows("shifts")], hide_index=True, width="stretch")
    with absence_tab:
        st.dataframe([{"Intervenant": a["cleaner_id"], "Début": display(a["start_at"]), "Fin": display(a["end_at"])}
                      for a in db.rows("absences")], hide_index=True, width="stretch")

elif page == "Journal d’audit":
    st.write("Avant/après, motif et auteur de chaque approbation locale. Les absences déclarées sont également tracées.")
    audits = list(reversed(db.rows("audit")))
    st.metric("Réaffectations approuvées", sum(a["action"] == "reassignment_approved" for a in audits))
    for audit in audits:
        title = f"#{audit['id']} · {'Réaffectation approuvée' if audit['action'] == 'reassignment_approved' else 'Indisponibilité déclarée'} · {display(audit['occurred_at'])}"
        with st.expander(title, expanded=audit["action"] == "reassignment_approved"):
            st.caption(f"Opérateur : {audit['operator']} · clé unique : {audit['event_key']}")
            st.write(audit["reason"])
            before, after = st.columns(2)
            before.markdown("**Avant**")
            before.json(json.loads(audit["before_json"]), expanded=True)
            after.markdown("**Après**")
            after.json(json.loads(audit["after_json"]), expanded=True)
    st.caption("Journal applicatif local ; pas de signature, d’authentification ni de garantie d’intégrité contre une modification directe du fichier.")

else:
    st.markdown("""### Le parcours de démonstration
1. Dans la barre latérale, simuler **C01, le 10 novembre 2026 de 08:00 à 17:00**.
2. Choisir **B001**, lancer l’analyse et examiner le classement ainsi que les exclusions.
3. Retenir **C02**, cocher la validation humaine et approuver la réaffectation simulée.
4. Lire le brouillon non envoyé, répéter l’approbation et ouvrir le journal.
5. Choisir **B002** et analyser : aucun remplaçant ne respecte toutes les règles.
6. Choisir **B014** : l’annulation à 24 heures reste une décision humaine.

### Ce que cette maquette permet de tester
Hypothèse non validée : une file explicable et traçable pourrait réduire l’effort de coordination.
Les compteurs représentent uniquement l’état fictif. Aucune économie réelle n’est démontrée.

### Règles fictives et limites
La région, la zone, la compétence, une plage couvrant toute la durée, les absences et les conflits
sont des contraintes strictes. Les intervalles sont semi-ouverts : une prestation finissant à
11:00 ne chevauche pas celle qui commence à 11:00. Aucun trajet ni temps de pause n’est garanti.
Les créneaux traversant minuit sont comparés en UTC. Les heures locales ambiguës ou inexistantes
sont refusées à la saisie. Le seuil de 48 heures utilise une durée écoulée, y compris lors du
changement d’heure ; à exactement 48 heures, aucun indicateur de retard n’est ajouté.

Une approbation ne prouve ni l’accord du client ni celui de l’intervenant. Aucun envoi, paiement,
changement de compte réel ou annulation automatique n’existe dans ce prototype.

### Vérifier et reproduire
Les instructions sont dans README.md ; les tests dans tests/ ; le scénario vidéo dans
DEMO_SCRIPT.md. Le bouton de réinitialisation restaure le même jeu de données fictif.
L’horloge du scénario reste le 9 novembre 2026 à 08:00, même si la date réelle avance.
""")
    st.link_button("Source publique · continuité et remplacements", "https://menagesimple.com/a-propos-de-menagesimple/")
    st.link_button("Source publique · annulation jusqu’à 48 h", "https://menagesimple.com/questions-frequentes-menage/")

st.divider()
st.caption("Operations Rescue · Prototype de candidature indépendant · décision humaine requise · Europe/Zurich")
