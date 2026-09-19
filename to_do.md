# To-Do — Pistes d'amélioration

## 🔴 Bugs / risques à corriger en priorité

- [x] **Injection SQL généralisée** — `scripts/database_requests.py` construisait presque toutes les requêtes par f-string avec les entrées utilisateur interpolées directement. Corrigé : toutes les requêtes utilisent désormais des paramètres `?` (DuckDB). Seuls les chemins de fichiers CSV internes (non fournis par l'utilisateur) restent interpolés.
- [x] **Chemin de la base fragile** — `scripts/database_requests.py:8` utilise désormais `Path(__file__).resolve().parent.parent / "data" / "database.duckdb"`, cohérent avec le reste du code (`search_contract.py:90`).
- [x] **Fonction dupliquée** — `get_contract_accepted` définie deux fois à l'identique (`database_requests.py:56-65` et `67-76`), code mort qui prête à confusion.
- [ ] **Bugs probables dans `shop.py`** — `tabs/shop.py:57` (`get_user_location(user_id)[0][0]`, incohérent avec le `.loc[...]` utilisé ailleurs) et ligne 62 (indexation positionnelle sur une colonne nommée) risquent de lever des `KeyError`.

## 🟠 Hygiène de projet

- [ ] **Scripts de debug committés dans `scripts/`** — `test.py` (modifie le wallet en prod !) et `testo.py` (code cassé, `NameError`) devraient soit devenir de vrais tests `pytest` dans un dossier `tests/`, soit être supprimés.
- [ ] **Gros fichiers/état versionnés** — `data/database.duckdb` (2,9 Mo, état de session utilisateur) devrait être dans `.gitignore` ; `airports.csv` (12,6 Mo) et `runways.csv` (3,9 Mo) gagneraient à passer en Git LFS ou téléchargement à l'installation plutôt qu'en tracking git direct.
- [ ] **Aucune CI/tests** — pas de `.github/workflows`, pas de suite pytest réelle.

## 🟡 Fonctionnel / dette

- [ ] `tabs/bank.py` est quasiment vide — onglet visible dans l'UI mais non implémenté.
- [ ] `user_id = 1` en dur (`app.py:27`) — pas d'authentification, cohérent avec ce que note déjà le README.
- [ ] Code de carte Folium dupliqué entre `contracts.py` et `flight.py` — à mutualiser dans un helper commun.
- [ ] Aucun typing, gestion d'erreurs inégale (`try/except Exception` générique par endroits, absente dans `database_requests.py`).

## ✅ Points forts à noter

- Le split récent d'`app.py` en modules `tabs/` va dans la bonne direction.
- La séparation UI/logique est amorcée.
- Le README a déjà une section "améliorations possibles" plutôt lucide.
