# To-Do — Pistes d'amélioration

## 🔴 Bugs / risques à corriger en priorité

- [x] **Injection SQL généralisée** — `scripts/database_requests.py` construisait presque toutes les requêtes par f-string avec les entrées utilisateur interpolées directement. Corrigé : toutes les requêtes utilisent désormais des paramètres `?` (DuckDB). Seuls les chemins de fichiers CSV internes (non fournis par l'utilisateur) restent interpolés.
- [x] **Chemin de la base fragile** — `scripts/database_requests.py:8` utilise désormais `Path(__file__).resolve().parent.parent / "data" / "database.duckdb"`, cohérent avec le reste du code (`search_contract.py:90`).
- [x] **Fonction dupliquée** — `get_contract_accepted` définie deux fois à l'identique (`database_requests.py:56-65` et `67-76`), code mort qui prête à confusion.
- [x] **Bugs probables dans `shop.py`** — `tabs/shop.py:57` (`get_user_location(user_id)[0][0]`, incohérent avec le `.loc[...]` utilisé ailleurs) et ligne 62 (indexation positionnelle sur une colonne nommée) risquent de lever des `KeyError`.


## 🟡 Fonctionnel / dette

- [ ] Code de carte Folium dupliqué entre `contracts.py` et `flight.py` — à mutualiser dans un helper commun.
- [x] Ajouter la gestion d'utilisateurs et une authentification
- [x] ajouter une navbar sur la gauche
- [ ] Ajouter la gestion du carburant
- [ ] Dans le hangar, ajouter la possibilité de mettre du carburant et faire l'entretien
- [ ] Ajouter un calculateur de consomation. entrée : distance en nm, et sortie : quantitée consommé en gal
- [ ] Rajouter des nouveaux types de contrats
- [ ] Dans la banque, ajouter la possibilité de contracter un credit
- [ ] Dans la banque, ajouter les logs (gains et pertes)
- [ ] Separer l'onglet flight en deux : free flight, contracts
- [ ] Dans l'onglet free flight et dans l'onglet contracts, ajouter les logs liés au vol connecté a l'api MSFS2024
