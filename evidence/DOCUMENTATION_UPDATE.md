# Mise à jour documentaire après le compte rendu externe

Vérifications exécutées par Codex sur les fichiers livrés :

- SHA-256 de l’archive initiale inchangé : `1e783a1650fb3252fafb35ef642d6821ad2c27b9f254e9069ff625f380f16205`.
- **13 fichiers exécutables/de configuration comparés octet par octet** au ZIP
  initial : application, modules, tests, lanceur, configuration Streamlit et dépendances.
  Tous sont identiques. Aucun ajout de fonctionnalité.
- Les huit séquences du storyboard sont contiguës, de 0:00 à **2:40** : **160 secondes**
  planifiées, **20 secondes** de réserve sous la limite. La narration comporte environ
  **262 mots**, hors actions ; ce calcul ne remplace pas une répétition ni la mesure vidéo.
- Les étapes B001/B002/B014, le choix déterministe, l’identité et le consentement sont présents.
- Les tests n’ont pas été relancés pour ces seuls changements de documents. Le résultat local
  conservé est 45 réussites en 14,62 s ; le résultat externe de 2,14 s reste attribué à la revue.

Une nouvelle archive `OperationsRescue-submission.zip` réunit les mêmes sources et les
documents actualisés. `OperationsRescue.zip`, déjà inspecté dans la revue externe, est conservé.

Fichiers comparés :

- `.streamlit/config.toml`
- `app.py`
- `domain.py`
- `matching.py`
- `requirements.txt`
- `seed.py`
- `START-DEMO.cmd`
- `store.py`
- `tests/conftest.py`
- `tests/test_app.py`
- `tests/test_incidents.py`
- `tests/test_matching.py`
- `tests/test_time_rules.py`
