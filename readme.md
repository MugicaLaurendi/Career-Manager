# Career Manager

## Description

Career Manager est une application Streamlit interactive pour gérer des missions aériennes fictives. L'utilisateur peut rechercher des contrats depuis un aéroport de départ, visualiser les destinations sur une carte et consulter les détails des contrats.

L'application utilise:
- `Streamlit` pour l'interface utilisateur
- `Folium` et `streamlit-folium` pour la carte interactive
- `DuckDB` pour la gestion locale de la base de données
- `Pandas` pour la manipulation des données

## Fonctionnalités

- Recherche d'aéroports par code OACI
- Génération de contrats de type `Cargo`, `Passenger` ou `Tourism`
- Filtrage des contrats par catégorie et distance
- Carte interactive avec les aéroports et itinéraires
- Base de données DuckDB pour stocker les contrats acceptés, l'historique, les utilisateurs et les aéronefs

## Installation

1. Ouvrir un terminal dans le dossier du projet `Career-Manager`
2. Installer les dépendances Python:

```bash
pip install -r requirements.txt
```

## Utilisation

### Lancer l'application

Sous Windows, exécutez:

```batch
start.bat
```

Ou directement si vous préférez:

```bash
streamlit run app.py
```

### Structure du projet

- `app.py` : interface principale Streamlit
- `requirements.txt` : dépendances Python
- `start.bat` : script de démarrage Windows
- `data/airports.csv` : base de données des aéroports
- `data/database.duckdb` : base DuckDB persistante
- `scripts/init_database.py` : script d'initialisation de la base de données
- `scripts/search_contract.py` : recherche d'aéroport et génération de contrats
- `scripts/database_requests.py` : opérations DuckDB pour les contrats et l'utilisateur

## Base de données

Le projet utilise une base DuckDB locale située dans `data/database.duckdb`.

Le script `scripts/init_database.py` crée les tables suivantes :
- `contracts_accepted`
- `contracts_historical`
- `users_aircrafts`
- `users`

Il insère également un utilisateur de test et un aéronef d'exemple.

## Dépendances

Les bibliothèques principales sont :

- `streamlit`
- `folium`
- `streamlit-folium`
- `duckdb`
- `pandas`

## Notes

- Le code actuel utilise un utilisateur fixe `user_id = 1`. Une authentification réelle peut être ajoutée ultérieurement.
- La génération des contrats est aléatoire et dépend des données présentes dans `data/airports.csv`.
- Les opérations de base de données utilisent des chemins relatifs vers `data/database.duckdb`.

## Améliorations possibles

- Ajouter la gestion d'utilisateurs et une authentification
- Permettre l'acceptation réelle d'un contrat et la mise à jour du portefeuille
- Ajouter des détails de l'aéronef et un hangar actif
- Optimiser la génération des contrats et les filtres de recherche
