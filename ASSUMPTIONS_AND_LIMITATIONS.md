# Faits publics, hypothèses et limites

Consultation des trois pages officielles le **8 novembre 2026**. Elles décrivent une offre
client, pas le fonctionnement interne, les outils de coordination ou un problème avéré.

## Ancrages publics vérifiés

| Fait public retenu | Source | Conséquence limitée pour la maquette |
| --- | --- | --- |
| Le service privilégie la continuité et organise des remplacements si nécessaire. | [À propos](https://menagesimple.com/a-propos-de-menagesimple/) | La continuité apparaît comme critère de classement fictif. |
| La FAQ mentionne l’annulation gratuite jusqu’à 48 heures avant le ménage. | [FAQ](https://menagesimple.com/questions-frequentes-menage/) | Un indicateur de revue humaine existe en deçà de 48 h ; aucun frais ni remboursement n’est inféré. |
| Un site/application client et l’assistante téléphonique MarIA existent déjà. | [Accueil](https://menagesimple.com/) | Le périmètre est un poste opérateur de démonstration, sans nouveau système de réservation ou assistant client. |

La FAQ présente les clients comme employeurs des intervenants. **Agent** et **intervenant**
désignent ici des identifiants synthétiques ; aucun statut d’emploi interne n’est supposé.

## Hypothèses opérationnelles à valider

- Une équipe pourrait trouver utile une file de perturbations avec alternatives explicables.
  Aucun entretien, journal d’activité ni délai réel de traitement n’a été collecté.
- Une prestation exige une seule personne, une compétence, une région et une zone.
  Les régions Vaud, Genève et Fribourg sont des noms publics ; les zones A/B/C et les foyers
  F001–F018 sont inventés. Aucune adresse ni distance n’est représentée.
- Une plage de travail unique doit couvrir toute la durée de la prestation. Des plages
  consécutives distinctes ne sont pas fusionnées : revue humaine conservatrice si besoin.
- Les contraintes sont strictes : région, zone, compétence, plage complète, absence et
  réservation en conflit. Un incident non résolu réserve toujours son créneau existant.
- Les intervalles sont semi-ouverts `[début, fin)` : deux prestations adjacentes ne se
  chevauchent pas. **Cela ne valide aucun déplacement ni aucune pause**. L’opérateur doit
  les vérifier. Ajouter une marge sans source aurait donné une fausse précision.
- Les candidats admissibles sont triés par continuité du foyer (oui avant non), nombre
  d’autres prestations intersectant le jour local, puis identifiant alphabétique. Ce n’est
  ni une optimisation de tournée, ni un classement de qualité ou de personnes réelles.
- Le seuil de revue tardive utilise `< 48 heures` écoulées en UTC : exactement 48 heures
  n’est pas marqué tardif. La convention à la seconde près est une **hypothèse de maquette**,
  pas une interprétation complète des conditions commerciales. Les demandes passées
  sont également signalées pour revue ; aucune annulation n’est exécutée.
- Le scénario fixe l’horloge au 9 novembre 2026, 08:00 Europe/Zurich. Les événements audit
  utilisent cette horloge synthétique et un identifiant séquentiel, pas une preuve de date réelle.
- Une personne clique explicitement pour approuver. Il n’y a aucune acceptation implicite
  du foyer ou de l’intervenant ; le bouton ne prouve pas leur consentement.

## Schéma de données

Source exécutable de référence : `SCHEMA` dans `store.py`. Toutes les bornes temporelles
sont stockées comme ISO 8601 UTC normalisé ; l’affichage et la saisie utilisent Europe/Zurich.

| Table | Champs essentiels et invariants |
| --- | --- |
| `meta` | clé/valeur : marqueur de base fictive, version du seed, horloge et jeton de génération |
| `cleaners` | ID, libellé inventé, région, zone, compétences JSON |
| `shifts` | intervenant, début/fin UTC, durée positive, unicité du créneau |
| `bookings` | ID, foyer synthétique, région/zone, service, début/fin, intervenant, version |
| `history` | couple foyer/intervenant unique : continuité synthétique connue |
| `absences` | intervenant et fenêtre UTC ; même déclaration exacte unique |
| `incidents` | prestation, type, intervenant d’origine, état, raison, dates, candidat approuvé |
| `audit` | clé d’événement unique, incident, action, JSON avant/après, date, `demo_operator`, motif |
| `drafts` | un brouillon par incident approuvé ; seul état permis : `draft_not_sent` |

États : `needs_review` à la création ; `candidate_found` ou `unresolved` après analyse ;
`approved` après décision locale. Le dossier d’annulation reste `needs_review`.
Un index interdit plusieurs incidents d’absence ouverts pour la même prestation. La clé
prestation/type/intervenant d’origine empêche une répétition du même dossier. Une nouvelle
absence du remplaçant peut créer un nouveau dossier lié à sa propre affectation.

## Garanties démontrées et frontières

L’approbation prend un verrou d’écriture SQLite avec `BEGIN IMMEDIATE`, vérifie le jeton de
génération et la version attendue, relit toutes les contraintes et enregistre affectation,
incident, audit et brouillon dans la même transaction. Deux approbations concurrentes
pour un candidat sur des créneaux qui se chevauchent ne réussissent pas toutes les deux.
Une répétition du même incident et du même candidat est sans effet. Un candidat différent
sur un incident déjà approuvé est refusé. Une erreur lors de la sauvegarde du brouillon
annule également l’affectation et le journal.

Ces garanties concernent **les écritures passant par `Store`**. Un utilisateur peut modifier
directement le fichier SQLite : le prototype ne fournit ni contrôle d’accès, ni journal
inviolable, ni mécanisme complet de sécurité de production. Les transactions ne valent pas
preuve d’autorisation juridique ou contractuelle. L’identité `demo_operator` est un libellé fixe.

La saisie locale refuse les heures inexistantes au printemps et ambiguës à l’automne.
Les fonctions du domaine savent comparer des instants explicitement décalés et des
prestations traversant minuit. Le jeu principal ne contient pas de service nocturne ; ces
cas sont démontrés par les tests et ne constituent pas des besoins métier confirmés.

## Avant d’envisager une utilisation réelle

1. Observer, avec accord de l’entreprise, quelques cas anonymisés d’absence ; vérifier que
   cette file ajoute une valeur aux outils déjà en place, y compris aux escalades de MarIA.
2. Faire valider zones, compétences, horaires, consentements, déplacements, pauses,
   conditions commerciales et traitement des annulations par les responsables concernés.
3. Comparer en observation parallèle le temps de traitement, les reprises manuelles et
   les erreurs d’affectation à une référence définie à l’avance ; ne pas convertir le seed
   en promesse d’économie.
4. Définir authentification, autorisations, confidentialité, rétention, intégrité du journal,
   sauvegardes, reprise après panne, accessibilité et intégrations avant toute donnée réelle.

Aucun de ces travaux de validation métier ou de production n’a été réalisé dans cette maquette.
