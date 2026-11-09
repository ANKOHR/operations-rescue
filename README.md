# Operations Rescue

Prototype local d’aide à la décision pour une étude de cas MénageSimple. Interface en français,
Python 3.11+, Streamlit et SQLite. **Données fictives uniquement. Aucun message envoyé.**

## Problème et hypothèse de valeur

Une absence peut obliger une équipe à revoir plusieurs prestations. Cette maquette teste une
hypothèse : regrouper les dossiers, expliquer les alternatives et tracer une décision humaine
pourrait réduire l’effort de coordination et aider à éviter des affectations en conflit.
Ce besoin interne et ces bénéfices n’ont pas été validés avec MénageSimple ; aucun gain réel
n’a été mesuré. Le prototype complète un scénario opérateur, sans recréer le système de
réservation ou MarIA.

Le contexte public a été vérifié le 8 novembre 2026 : [présentation de l’entreprise](https://menagesimple.com/a-propos-de-menagesimple/),
[site et services existants](https://menagesimple.com/), [FAQ](https://menagesimple.com/questions-frequentes-menage/).
Les règles fictives et leurs limites sont détaillées dans [ASSUMPTIONS_AND_LIMITATIONS.md](ASSUMPTIONS_AND_LIMITATIONS.md).

## Installation et démarrage

Depuis **ce dossier**, dans PowerShell sous Windows :

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Utiliser `py -3.12` ou `py -3.11` si nécessaire. Sur la machine de construction, `python`
désigne Python 3.10 : utiliser le lanceur `py -3.13`, puis l’interpréteur du venv.
Le raccourci **START-DEMO.cmd** choisit une version installée 3.13, 3.12 ou 3.11, crée le venv
au premier démarrage, installe les trois dépendances directes et ouvre l’application.

Sur macOS/Linux avec Python 3.11+ :

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

Adresse par défaut : **http://127.0.0.1:8501**. La session de vérification a utilisé le port
8517. Pour changer de port, ajouter `--server.port 8517`. Arrêter avec `Ctrl+C` dans le terminal.
Après installation des paquets, le parcours fonctionne hors ligne. Pas de compte, clé API,
endpoint IA, Docker ou hébergement. Les liens documentaires publics sont facultatifs.
Le serveur est limité à `127.0.0.1` et la télémétrie Streamlit est désactivée dans
`.streamlit/config.toml`. Lancer depuis ce dossier pour charger cette configuration.

Versions directes effectivement vérifiées : Python 3.13.5, Streamlit 1.67.0,
pytest 9.2.0, tzdata 2026.6. Voir `evidence/environment.txt` pour la capture exacte et
`requirements.txt` pour les versions directes épinglées. Les dépendances transitives
sont capturées dans `evidence/pip-freeze.txt` ; ce fichier n’est pas une garantie de compatibilité
sur tous les systèmes.

## Orientation en deux minutes

1. Le premier lancement crée **8 intervenants, 18 prestations, 3 absences et 4 dossiers**.
   Le dossier B014 est une annulation fictive à 24 heures : le bouton automatique est désactivé.
2. Dans la barre latérale, garder **C01**, début `2026-11-10 08:00`, fin `2026-11-10 17:00`,
   puis **Simuler l’absence**. Deux nouveaux dossiers concernent B001 et B002 ; répéter
   cette simulation ne les duplique pas.
3. B001 est sélectionné. Cliquer **Analyser les remplacements**. C02 arrive avant C03 :
   continuité du foyer, puis charge journalière et identifiant stable. Déplier les exclusions.
4. Retenir C02, lire les limites, cocher la validation, puis **Approuver la réaffectation simulée**.
   La réservation locale passe de C01 à C02 ; un événement avant/après et un brouillon sont
   enregistrés atomiquement. Le bouton de répétition ne crée aucun doublon.
5. Choisir B002 et analyser : **aucun candidat admissible** ; les huit exclusions restent visibles.
6. Ouvrir **Journal d’audit**, puis **Planning & disponibilités** pour vérifier l’affectation.

Les compteurs concernent les incidents, pas des économies ni un taux réel de réussite.
L’horloge reste le **9 novembre 2026 à 08:00 Europe/Zurich**. Les dates ne suivent pas le jour réel.

## Tests et remise à zéro

```powershell
.\.venv\Scripts\python.exe -m pytest -q --junitxml=evidence\pytest-results.xml
.\.venv\Scripts\python.exe seed.py --reset-demo
```

Le bouton **Outils de démonstration → Réinitialiser la démo** restaure également le jeu initial
en une action. Il remplace uniquement les tables de la base appartenant à cette démo
(`data/demo.sqlite3`). Il refuse une base remplie sans son marqueur de propriété. Aucun fichier
externe n’est effacé. Le contenu métier est déterministe ; seul le jeton de génération du jeu
change pour refuser une approbation issue d’un onglet antérieur à la remise à zéro.

**45 tests observés comme réussis** lors de la vérification documentée. Ils couvrent les règles
de temps, le classement, les exclusions, la revalidation transactionnelle, les répétitions,
les accès concurrents, le rollback et le parcours Streamlit. Les tests utilisent des bases
temporaires et ne remettent pas la démo de l’utilisateur à zéro.
Les résultats frais et les contrôles Chrome sont dans [evidence/VERIFICATION.md](evidence/VERIFICATION.md).
Un compte rendu de revue fourni par Henry rapporte aussi **45/45 tests en 2,14 s sous
Python 3.12.14 / Linux**. Cette exécution externe n’a pas été observée par Codex et ne
remplace pas la revue personnelle de Henry. Voir [evidence/EXTERNAL_REVIEW.md](evidence/EXTERNAL_REVIEW.md).

## Architecture

| Module | Responsabilité |
| --- | --- |
| `domain.py` | Instants UTC, saisie/affichage Zurich, chevauchements, seuil de 48 heures |
| `matching.py` | Contraintes pures, raisons, classement stable, gabarits de brouillons |
| `store.py` | SQLite, absence, analyse, approbation sérialisée, journal et brouillon atomiques |
| `seed.py` | Jeu synthétique fixe, initialisation, reset atomique |
| `app.py` | Interface française ; les écritures passent par `Store` |
| `tests/` | Tests du domaine, de la persistance et du vrai runner Streamlit |

Il n’existe ni client de messagerie, ni file d’envoi, ni mutation sur un système réel.
L’IA a aidé à construire et contrôler la maquette ; le moteur exécuté dans l’application reste
déterministe. Voir [AI_USAGE_AND_VERIFICATION.md](AI_USAGE_AND_VERIFICATION.md).

## Démonstration vidéo

Le [parcours commenté](https://youtu.be/xdnpvGG7hsY) dure **160,02 secondes**. Il montre
la simulation d’absence, le classement explicable, la validation humaine, le journal et les
deux cas où aucune automatisation n’est forcée. L’interface est en français ; la narration
et les sous-titres sont en anglais. La vidéo indique explicitement que le parcours a été
opéré par une IA et que la voix est synthétique.

Henry a confirmé ses propres contrôles de B001, B002, B014 et des tests, dans la portée
précise consignée dans [evidence/PERSONAL_VERIFICATION.md](evidence/PERSONAL_VERIFICATION.md).
Les vérifications liées à la vidéo sont dans
[evidence/VIDEO_VERIFICATION.md](evidence/VIDEO_VERIFICATION.md).

Ce dépôt est une étude de cas indépendante. Il n’est pas affilié à MénageSimple et ne
représente ni un outil déployé ni une validation par ses équipes.
