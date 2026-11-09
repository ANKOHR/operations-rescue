# Vérification observée

Date : 8 novembre 2026. Agent de construction : Codex. Données publiques ou fictives uniquement.
Les contrôles ci-dessous ne constituent pas une revue humaine indépendante.

## Tests exécutés

- Premier lot : **40 passed in 12.12s** (domaine, classement, persistance).
- Deuxième lot : **45 passed in 16.86s**, avec cinq parcours via le runner officiel
  `streamlit.testing.v1.AppTest`. Aucun mock des écritures métier.
- Résultat final après les corrections UI : **45 passed in 14.62s** ; voir `pytest-output.txt` et `pytest-results.xml`.
  Ces fichiers donnent la sortie exacte et la durée de la dernière exécution.
- L’environnement et les dépendances observés sont dans `environment.txt` et `pip-freeze.txt`.

## Revue externe rapportée

Le compte rendu fourni ensuite par Henry rapporte **45/45 tests en 2,14 s sous Python
3.12.14 / Linux**, sans défaut critique identifié dans la démonstration implémentée.
Cette exécution n’a pas été observée par Codex ; ses logs bruts ne sont pas inclus.
Voir `EXTERNAL_REVIEW.md` pour la provenance et `DOCUMENTATION_UPDATE.md` pour la comparaison
du code livré après les modifications documentaires. La confirmation personnelle reçue
ensuite pour les trois scénarios et les tests est consignée dans `PERSONAL_VERIFICATION.md`.

| Risque | Preuve automatisée |
| --- | --- |
| Mauvaise région, zone ou compétence | Raisons d’exclusion testées individuellement |
| Disponibilité partielle ou prestation existante | Couverture intégrale du créneau et conflits testés |
| Absence déclarée après analyse | Approbation refusée au recontrôle |
| Conflit ajouté après analyse | Refus ; aucun audit d’approbation ni brouillon créé |
| Deux requêtes visant le même candidat | Deux connexions concurrentes ; une seule approbation réussit |
| Erreur d’écriture du brouillon | Échec injecté ; affectation, incident et audit restaurés par rollback |
| Double clic, répétition, second candidat | Répétition idempotente ; autre candidat refusé |
| Répétition d’absence et fenêtres qui se recouvrent | Pas de duplication du dossier ouvert |
| Heure locale et seuil commercial | UTC, minuit, heure d’été/hiver, frontière exacte de 48 h |
| Analyse prise pour une approbation | Analyse sans mutation de réservation ; approbation UI nécessite la case humaine |
| Reset avec un ancien onglet | Jeton de génération ancien refusé |
| Écrasement d’une autre base | Reset d’une base remplie non marquée refusé |
| Dossier sans candidat ou annulation | Aucune affectation forcée ; annulation automatique absente |

## Contrôles manuels via Chrome

Serveur de vérification : `http://127.0.0.1:8517`, limité à la boucle locale. Le navigateur
était d’abord dans une fenêtre étroite d’environ 709 px de large, puis dans une fenêtre
d’environ 1463 px. Le panneau latéral se replie dans la première et reste lisible dans la seconde.

| Parcours | Observation |
| --- | --- |
| Premier écran | Bandeau données fictives, horloge fixe, 4 dossiers ; B014 montre la revue <48 h et le bouton automatique désactivé. |
| Simulation C01, 10/11 08:00–17:00 | Message de 2 nouveaux dossiers ; B001 et B002 présents. |
| B001 analysé | C02 en tête par continuité ; C03 deuxième ; 6 intervenants exclus avec raisons. |
| Sélection après changement d’état | Une première version pouvait revenir à B014 ; corrigé par des libellés stables et parcours répété. |
| Validation B001 | Case humaine cochée, approbation explicite ; C01 → C02 affiché, brouillon non envoyé visible. |
| Répétition B001 | Message « Déjà approuvé » ; aucune nouvelle affectation, aucun événement ni brouillon. Contrôle SQLite complémentaire du nombre d’événements. |
| B002 analysé | État « Sans solution » ; explication pour les 8 intervenants, dont plage partielle de C06 et conflit B008 de C07. |
| Journal | Dans Chrome : une approbation, opérateur `demo_operator`, B001, C01/version 0 avant et C02/version 1 après. |
| Planning et aide | AppTest ouvre ces vues sans exception. |
| Reset et saisie invalide | AppTest restaure 4 dossiers et refuse une fenêtre dont la fin précède le début. |
| Dernier état navigateur | Aucune erreur dans les 10 dernières entrées de niveau erreur de la session Chrome contrôlée. Ce constat n’est pas un audit exhaustif du navigateur. |

Captures : `approval-idempotence.jpg`, `no-safe-match.jpg` et `audit.jpg`.
Elles montrent des états de démonstration vérifiés, pas des données réelles.
`demo-state.json` conserve l’état synthétique observé : une approbation, un seul brouillon
non envoyé et B002 non résolu. Après capture, la base locale a été restaurée à ses 4 dossiers
initiaux pour la prise en main. L’archive ne contient aucune base mutable ; elle recrée le seed.

## Limites des contrôles

Pas de test exhaustif des navigateurs, de charge, de sécurité, d’accessibilité, de sauvegarde
ou de migration. Pas de consentement réel ni d’échange client. Le besoin métier n’est pas
confirmé et aucun retour d’opérateur n’a été obtenu. Une copie vidéo de revue a ensuite été
enregistrée par IA et publiée en non répertorié ; voir `VIDEO_VERIFICATION.md`. Cette copie
ne constitue pas en elle-même une revue personnelle de Henry. Sa confirmation ultérieure
pour B001, B002, B014 et les tests est documentée séparément.
