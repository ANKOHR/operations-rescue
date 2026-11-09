# Vidéo de revue — capture et hébergement observés

**Version courante : https://youtu.be/xdnpvGG7hsY**

Cette étape a été effectuée par Codex à la demande de Henry. Elle ne constitue pas une
relecture humaine indépendante. Henry a ensuite confirmé personnellement les trois scénarios
et les tests ; cette déclaration distincte est consignée dans `PERSONAL_VERIFICATION.md`.
La dernière scène et sa narration ont été remplacées pour refléter sa confirmation.

## Capture et narration

- Application extraite de `OperationsRescue-submission.zip` dans un dossier de travail,
  base fictive restaurée et serveur limité à la boucle locale.
- Capture du véritable onglet de l’application par l’API navigateur, **4 images/seconde**,
  huit séquences montées selon le minutage de 160 secondes. Aucun écran de données réelles.
- Parcours observés : création de deux incidents, classement de B001, case opérateur,
  approbation C01 → C02, brouillon non envoyé, répétition idempotente, journal avant/après,
  B002 sans candidat et B014 avec annulation automatique indisponible.
- Les 45 tests ont réussi de nouveau sur Windows / Python 3.13.5 : **45 passed in 22.20s**.
  L’écran final de preuves est une vue du véritable rapport JUnit, explicitement présentée
  comme telle. La durée propre de la suite JUnit est 22,139 s.
- Narration anglaise synthétique locale, voix Microsoft Zira Desktop, sans imitation de Henry.
  Bandeau continu d’attribution à l’IA, chapitres et sous-titres anglais intégrés à l’image.
- L’interface française, les données fictives, le code et les tests de l’application n’ont
  pas été modifiés pour produire la vidéo.

## Contrôles du fichier

| Élément observé | Résultat |
| --- | --- |
| Fichier | `OperationsRescue-demo-reviewed.mp4`, fourni séparément du code |
| Taille | 5 048 624 octets |
| Durée décodée | **160,02 secondes**, inférieure à 180 secondes |
| Image | H.264, 1920 × 1080, 24 images/seconde après encodage |
| Audio | AAC ; présence et niveau contrôlés, crête à −6 dB |
| Décodage intégral | Aucune erreur signalée par FFmpeg |
| Contrôle visuel | Images extraites du fichier monté : validation cochée, audit C01/C02 et annulation conservée lisibles |

Les captures sources sont espacées à 4 images/seconde : les mouvements et transitions ne
sont pas une capture haute fréquence. Les sous-titres suivent la narration synthétique.
Codex n’a pas effectué une écoute humaine intégrale ; Henry doit regarder et écouter la vidéo
pour juger le rythme, la prononciation et son adéquation à la candidature.

## Hébergement observé

- Compte YouTube déjà connecté, chaîne **HNRY** ; aucune création de compte.
- Titre courant : `Operations Rescue | MenageSimple walkthrough (2:40)`.
- Visibilité **Unlisted / Non répertoriée** sélectionnée avant sauvegarde.
- Déclaration d’usage de l’IA activée, absence de promotion payante indiquée,
  notifications aux abonnés désactivées.
- YouTube Studio a affiché « Video published ». La page de lecture a affiché le titre,
  **Unlisted** et **AI: Content was made with AI**, avec la lecture progressant à 0:03 / 2:40.
- La lecture a été vérifiée dans la session connectée. Aucun test distinct déconnecté n’a
  été effectué. Les contrôles YouTube ont affiché « No issues found » au moment de l’envoi ;
  cela ne garantit pas l’absence de problème ultérieur.

Aucun message n’a été envoyé à un recruteur et aucun formulaire Typeform n’a été soumis.
Le lien du dépôt/code reste à compléter après le choix du mode de partage par Henry.

## Révision après confirmation de Henry

- Déclaration reçue dans le chat pour B001, B002, B014 et les tests ; aucun journal personnel brut fourni.
- Les sept premières scènes sont inchangées. La dernière affiche désormais « Henry confirmed
  personal checks: B001, B002, B014 and tests » et la narration rapporte la même confirmation.
- Même durée de 160,02 s, décodage intégral sans erreur et contrôle visuel d’une image à 2:30.
- Original MP4 conservé, SHA-256 `cf3503abb3febcc91ffaa457dff117302a20162fd153d7eba4eac4ca647a8aee`.
- Nouveau MP4, SHA-256 `d1c6392c78b05bad16be42e7ea8566bc0ac19d79759c8f48703146a3e4064d9e`.
- Nouvelle publication non répertoriée ; lecture, statut Unlisted et label AI vérifiés.
  Le réglage AI était bien enregistré ; le label de la page de lecture a été confirmé après actualisation.
- La revue externe du premier MP4 est rapportée dans `EXTERNAL_VIDEO_REVIEW.md` et n’est
  pas présentée comme une nouvelle inspection indépendante de cette dernière scène.
