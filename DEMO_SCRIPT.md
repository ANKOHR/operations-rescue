# Vidéo de démonstration — 160 secondes prévues

**Limite : 180 secondes.** Ce fichier conserve le storyboard français. Une copie de revue
de **160,02 secondes**, opérée par Codex avec narration anglaise synthétique et interface
française, est désormais [disponible en non répertorié](https://youtu.be/xdnpvGG7hsY).
La dernière scène rapporte la confirmation personnelle de Henry pour B001, B002, B014 et
les tests ; l’attribution de la navigation et de la narration à l’IA reste explicite.
Viser 2:40, garder 20 secondes de réserve et couper au plus tard à 3:00.
Le fil conducteur est une décision opérateur : repérer une absence, vérifier une proposition,
assumer une décision et reconnaître les situations qui restent à traiter humainement.

## Préparer avant d’enregistrer

1. Installer et lancer selon README.md, ouvrir le navigateur et fermer les onglets privés
   visibles dans la capture. Filmer uniquement l’application et une fenêtre de résultats de tests.
2. Exécuter `python -m pytest -q` avec le venv actif ; garder le résultat réellement obtenu
   visible pour la dernière séquence. Ne pas remplacer un échec par la capture livrée.
3. Réinitialiser via **Outils de démonstration → Réinitialiser la démo**. Vérifier 4 dossiers,
   8 intervenants et 18 prestations. Utiliser l’horloge fixe affichée, pas la date de l’ordinateur.
4. Navigation **File d’intervention**. Garder le panneau de simulation prêt avec C01,
   `2026-11-10 08:00` → `2026-11-10 17:00`. Sur petite fenêtre, ouvrir la barre latérale avec `»`.
5. Répéter une fois ce parcours. Préférer une fenêtre assez large pour les listes et un zoom
   lisible. Attendre la fin du rendu après chaque action ; ne pas cliquer pendant un rerun.
6. Henry a confirmé B001, B002, B014 et les tests. Ne pas étendre cette confirmation à un
   audit complet ou à des essais métier réels. Voir SUBMISSION_CHECKLIST.md.

## Storyboard et narration suggérée

| Temps | Actions exactes | Narration française |
| --- | --- | --- |
| 0:00–0:18 | Montrer le titre, le bandeau fictif et l’horloge. | « Une absence peut obliger une équipe à revoir plusieurs prestations. Cette maquette teste l’utilité d’une file explicable pour examiner ces décisions. Toutes les données sont fictives ; ni le besoin interne ni les gains ne sont validés. » |
| 0:18–0:33 | Barre latérale : **Simuler l’absence** avec les valeurs préparées. Montrer 2 nouveaux dossiers. | « Aster devient indisponible le 10 novembre. Deux prestations sont touchées. L’équipe dispose maintenant de deux dossiers à examiner, sans modifier automatiquement les affectations. » |
| 0:33–0:57 | B001 est sélectionné. **Analyser les remplacements**. Montrer C02 puis C03 et ouvrir brièvement les exclusions. | « Les règles vérifient région, zone, compétence, durée, horaires et conflits. Brume est prioritaire pour la continuité du foyer. Je garde ce calcul déterministe : des critères vérifiables et des exclusions explicites, plutôt qu’une décision d’affectation confiée à un LLM. » |
| 0:57–1:24 | C02 retenu, motif par défaut, cocher la validation humaine, **Approuver la réaffectation simulée**. Montrer C01 → C02 et le brouillon. | « Je vérifie le dossier avant de valider. Le système recontrôle la disponibilité dans la transaction, puis conserve l’audit et le brouillon non envoyé. Cette case représente une action humaine dans la démo ; elle ne prouve ni l’identité de l’opérateur ni l’accord du client. » |
| 1:24–1:40 | **Répéter la même approbation · test d’idempotence**. Ouvrir **Journal d’audit**, montrer avant/après. | « Répéter l’approbation ne crée aucun doublon. Le journal montre le changement, le motif et l’opérateur de démonstration. Aucun message n’est envoyé. » |
| 1:40–2:01 | Retour **File d’intervention**, choisir **B002**, **Analyser les remplacements**. Montrer **Sans solution**, C06 et C07 parmi les exclusions. | « Pour la seconde prestation, aucun candidat ne remplit toutes les règles. Flocon ne couvre pas la durée et Galet est déjà réservé. Le moteur refuse de forcer une affectation : l’équipe doit chercher une autre solution. » |
| 2:01–2:16 | Choisir **B014**. Montrer l’indicateur moins de 48 h et le bouton désactivé. | « Cette annulation à 24 heures reste également une décision humaine. La maquette signale le délai, conserve l’affectation et ne décide ni frais ni remboursement. » |
| 2:16–2:40 | Montrer les résultats réellement obtenus et la confirmation personnelle reçue. Terminer sur les limites métier. | « Les 45 tests couvrent notamment les conflits concurrents et les limites temporelles. Henry confirme ses contrôles de B001, B002, B014 et des tests. Ce parcours reste opéré et narré par IA. Le besoin métier, les trajets et les consentements réels restent à valider. » |

Durée totale prévue : **160 secondes**, soit 20 secondes de réserve sous le maximum.
Ce minutage est une cible de répétition, pas la durée mesurée d’une vidéo existante.
Si le rendu ou la navigation prend du retard, raccourcir la narration du journal. Ne pas
retirer l’approbation humaine, le cas sans solution ou la limite sur les gains non mesurés.

## Après l’enregistrement

Vérifier la durée réelle (≤180 s), la lisibilité et l’absence de données privées. Ajouter
le lien vidéo et, si vous le choisissez, le dépôt source dans SUBMISSION_SUMMARY.md.
Le parcours vidéo a été publié en non répertorié sur demande de Henry. Le partage du code
et la soumission restent à effectuer ; aucun formulaire n’a été envoyé.
