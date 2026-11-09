# Usage de l’IA et vérification

## Rôle effectif de l’IA

Codex, assistant OpenAI, a construit les modules Python, la base synthétique, l’interface,
les tests et ces documents à partir du brief fourni. Il a également consulté les trois
pages publiques officielles et exécuté les commandes et contrôles Chrome décrits dans
`evidence/VERIFICATION.md`. Aucun travail n’a été délégué à Kimi ou à un autre agent.

L’IA a proposé la séparation domaine/persistance/UI, les règles de classement et les scénarios
de test. Les choix opérationnels qui dépassent les pages publiques restent explicitement
des hypothèses. La rédaction française est assistée par IA et doit être relue par Henry avant
la candidature ; elle ne prétend pas reproduire un style personnel validé.

**L’application elle-même n’appelle aucun modèle.** Les alternatives sont calculées par des
règles déterministes, et les messages sont des gabarits français. Ajouter un classificateur
local ou un LLM n’aurait pas établi la qualité du moteur de remplacement dans ce périmètre.
Aucun service payant, compte réel, clé API ou donnée client n’a été utilisé.

## Trois vérifications contre les sources publiques

- Continuité et remplacements : vérifiés sur la [page de présentation](https://menagesimple.com/a-propos-de-menagesimple/).
  Cela soutient le thème du scénario, pas son algorithme ni l’existence d’un besoin interne.
- Seuil public de 48 heures : vérifié dans la [FAQ](https://menagesimple.com/questions-frequentes-menage/).
  La maquette garde une revue humaine et n’invente aucune conséquence financière.
- Outils client et MarIA : vérifiés sur l’[accueil](https://menagesimple.com/).
  La maquette n’est donc pas présentée comme un nouveau système de réservation ou assistant téléphonique.

Consultation : 8 novembre 2026. Aucun compte, système de production, dossier client ou
communication privée du recruteur n’a été consulté. Les informations d’échéance et de notation
proviennent du brief de Henry. Un compte rendu externe fourni ensuite par Henry indique avoir
comparé les exigences au courriel du recruteur du 5 novembre et confirme l’échéance ; Codex
n’a pas consulté ce courriel ni authentifié lui-même cette comparaison.

## Erreurs et surinterprétations corrigées

1. **Sélection dynamique dans l’interface.** La première version ajoutait l’état du dossier
   dans le libellé des options. Dans Chrome, une analyse pouvait réinitialiser la sélection,
   alors que les tests Streamlit passaient. Le libellé a été rendu stable ; le statut reste
   dans le dossier. Le parcours corrigé a ensuite permis l’approbation de B001 dans Chrome.
2. **Compatibilité logicielle.** La commande `python` locale utilise Python 3.10, sous le minimum
   demandé. Le build a été exécuté dans un venv Python 3.13 et la documentation désigne
   explicitement ce lanceur. Une tentative d’installation avant la fin de création du venv
   a échoué sans modifier le projet ; elle a été relancée une fois le venv prêt.
3. **Portée du mot « sûr ».** Un planning sans chevauchement ne démontre pas la faisabilité
   des trajets, l’accord des personnes ou une politique réelle de remplacement. Le produit
   affiche « admissible selon les règles de la démo » et rappelle ces contrôles humains.
   Les compteurs synthétiques ne sont jamais présentés comme des économies mesurées.

## Résultats constatés

Le premier lot domaine/persistance a donné **40 tests réussis**. Après ajout des cinq tests du
runner Streamlit : **45 tests réussis**. Le rapport final, la durée et l’environnement exacts
sont conservés dans `evidence/pytest-output.txt`, `evidence/pytest-results.xml` et
`evidence/environment.txt`. Les cas incluent une compétition entre deux connexions SQLite,
un conflit apparu après analyse et un échec injecté à l’écriture du brouillon.

Dans Chrome, l’agent a contrôlé la simulation de deux dossiers, l’analyse de B001, la validation
humaine, l’affectation C01 → C02, le brouillon non envoyé, une répétition sans doublon et le cas
B002 sans candidat avec ses exclusions. Le dossier d’annulation B014 a montré une décision
automatique indisponible. Les vues supplémentaires et le reset sont aussi vérifiés par AppTest.
Voir la matrice détaillée et les captures dans `evidence/VERIFICATION.md`.

## Compte rendu de revue externe fourni par Henry

Le compte rendu transmis dans le chat rapporte **45/45 tests réussis en 2,14 secondes sous
Python 3.12.14 / Linux**, une inspection de l’archive et aucun défaut critique identifié dans
la démonstration implémentée. Ces résultats sont attribués à ce compte rendu : Codex n’a
pas observé cette exécution et ne dispose pas de ses logs bruts. Voir `evidence/EXTERNAL_REVIEW.md`.

La recommandation de garder le périmètre technique a été retenue. Seuls les documents ont
été actualisés : storyboard réduit à 160 secondes, explication du moteur déterministe et
distinction entre clic opérateur, authentification et consentement. À cette étape, la revue
personnelle restait à faire. Henry a depuis confirmé B001, B002, B014 et les tests ; voir
`evidence/PERSONAL_VERIFICATION.md`. Le compte rendu externe seul ne prouve pas ces vérifications.

## Ce qui n’est pas une vérification humaine indépendante

Les tests et la navigation ont été exécutés par l’assistant IA, sur son propre code.
Ce sont des contrôles reproductibles et des observations, **pas une revue indépendante
par un ingénieur humain ou une validation métier**. La confirmation ultérieure de Henry
porte sur B001, B002, B014 et les tests. Elle est consignée comme déclaration de sa part,
sans inventer de sortie de tests personnelle ni revendiquer un audit complet du code.

Pas de test avec de vrais opérateurs, de données réelles, de mesure de ROI, de charge à grande
échelle, d’audit sécurité/accessibilité complet ou de certification multi-OS. L’exécution
Python 3.12 / Linux est rapportée par le compte rendu externe ; seul le build Python 3.13 /
Windows a été exécuté et observé localement par Codex.

## Copie vidéo de revue assistée par IA

À la demande de Henry, Codex a ensuite capturé le parcours de l’application extraite du ZIP
de soumission : B001 approuvé puis répété sans doublon, journal avant/après, B002 non résolu
et B014 conservé en revue humaine. Les images proviennent du vrai onglet local, capturé à
4 images/seconde et monté en huit séquences. Le code de l’application n’a pas été modifié.

La narration anglaise a été synthétisée localement avec Microsoft Zira Desktop ; elle ne
reproduit pas la voix de Henry. Des chapitres, sous-titres anglais et le bandeau « AI-operated
walkthrough | Synthetic narration » ont été ajoutés. La durée décodée est **160,02 secondes**.

La vidéo a été publiée en **non répertorié** sur YouTube avec déclaration d’usage de l’IA,
notifications aux abonnés désactivées, puis sa lecture et les labels ont été observés.
Lien courant : https://youtu.be/xdnpvGG7hsY. Les 45 tests ont de nouveau réussi localement
en 22,20 s avant la capture. Henry a ensuite confirmé ses propres contrôles des trois scénarios
et des tests et a demandé de retenir le parcours enregistré. La dernière scène et sa narration
ont été mises à jour pour rapporter cette confirmation ; les sept premières scènes restent
inchangées. L’attribution à l’IA reste visible et la vidéo ne prétend pas avoir été naviguée
ou narrée personnellement par Henry. La première version est conservée séparément.
Voir `evidence/VIDEO_VERIFICATION.md` pour les limites et les preuves de cette étape.

## Pourquoi la décision reste humaine

Le modèle de données ignore volontairement de nombreuses conditions réelles. Le moteur
peut proposer une compatibilité dans son monde synthétique, pas autoriser un changement
chez une personne réelle. L’opérateur doit examiner les limites et cliquer explicitement ;
les annulations et les cas sans solution restent hors automatisation. Tous les textes
restent des brouillons à revoir, et aucun mécanisme d’envoi n’est implémenté.
