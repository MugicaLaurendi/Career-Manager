# ✈️ Career Manager

Career Manager est une application web (Streamlit) de gestion de carrière de pilote. Vous choisissez un profil, acceptez des contrats générés aléatoirement autour de votre position, les réalisez avec votre avion, encaissez la récompense et investissez dans de nouveaux appareils.

Les données d'aéroports proviennent d'[OurAirports](https://ourairports.com/data/) et la base de jeu est un fichier DuckDB local : aucun serveur ni compte externe n'est nécessaire.

L'application se veut permissive. À terme, elle suivra vos actions dans Microsoft Flight Simulator 2024, mais ne sanctionnera aucun mouvement « anormal » : vous pouvez utiliser la téléportation.

## Fonctionnalités

- **Profils** : sélection, création (avec photo optionnelle) et suppression de profils pilotes. Il n'y a pas de mot de passe.
- **Contrats** : recherche depuis un aéroport (code OACI) avec filtres par type de contrat (`Cargo`, `Passenger`), catégorie d'aéroport de destination et fourchette de distance. Les résultats sont affichés sur une carte et dans un tableau, avec le détail du contrat sélectionné.
- **Vol** : suivi du contrat en cours sur une carte, validation (récompense créditée, position mise à jour) ou abandon, et historique des contrats. Un mode *Free flight* permet de se déplacer vers n'importe quel aéroport sans contrat.
- **Hangar** : fiche de l'appareil actif, liste des avions possédés et changement d'appareil actif.
- **Shop** : catalogue d'avions (miniatures, caractéristiques, prix). L'achat débite le portefeuille et place l'appareil dans le hangar d'un aéroport de votre choix.
- **Bank** : onglet présent mais pas encore implémenté.
- **Barre latérale** : photo de profil, portefeuille, avion actif, position actuelle et déconnexion.

## Installation

Prérequis : Python 3.10 ou plus récent.

```bash
pip install -r requirements.txt
```

## Lancement

Sous Windows, `start.bat` installe les dépendances puis lance l'application :

```batch
start.bat
```

Ou directement, depuis la racine du projet :

```bash
streamlit run app.py
```

Le lancement depuis la racine est important : certains chemins (par exemple `./data/aircraft.csv` dans le shop) sont relatifs au dossier courant.

## Structure du projet

```
Career-Manager/
├── app.py                      # Point d'entrée : login, sidebar et onglets
├── start.bat                   # Lancement Windows
├── requirements.txt
├── .streamlit/config.toml      # Thème de l'interface
├── tabs/                       # Un module par onglet / écran
│   ├── login.py                #   sélection et gestion des profils
│   ├── sidebar.py              #   informations du pilote
│   ├── contracts.py            #   recherche et acceptation de contrats
│   ├── flight.py               #   contrat en cours, free flight, historique
│   ├── hangar.py               #   avion actif et liste des avions
│   ├── shop.py                 #   achat d'avions
│   └── bank.py                 #   (à implémenter)
├── scripts/
│   ├── database_requests.py    # Requêtes DuckDB (utilisateurs, contrats, avions)
│   ├── search_contract.py      # Recherche d'aéroports et génération des contrats
│   ├── init_database.py        # Création des tables
│   ├── aircraft_image.py       # Images et miniatures des avions
│   └── profile_image.py        # Photos de profil
├── data/
│   ├── database.duckdb         # Base de jeu
│   ├── airports.csv            # Aéroports (OurAirports)
│   ├── runways.csv             # Pistes (OurAirports)
│   ├── aircraft.csv            # Catalogue d'avions du shop
│   ├── sources.md              # Sources des données
│   └── images/                 # aircrafts/, profiles/, placeholders/
└── tests/test_db.py            # Script de test manuel sur la base
```

## Base de données

La base `data/database.duckdb` est versionnée avec le projet. Elle contient quatre tables :

| Table | Rôle |
|---|---|
| `users` | Profils : nom, portefeuille, avion actif, position actuelle |
| `users_aircrafts` | Avions possédés par chaque pilote (carburant, maintenance, hangar, caractéristiques) |
| `contracts_accepted` | Contrat en cours de chaque pilote |
| `contracts_historical` | Contrats terminés (`completed`) ou abandonnés (`aborted`) |

`scripts/init_database.py` crée ces tables et insère un pilote de départ (position `LFCH`, 10 000 $) avec son premier avion (id 20 du catalogue).

## Dépendances

- `streamlit` : interface
- `folium` et `streamlit-folium` : cartes interactives
- `duckdb` : base de données locale et lecture des CSV
- `pandas` : manipulation des données
- `Pillow` : miniatures des avions et photos de profil

## Notes

- Les contrats sont générés aléatoirement à partir de `data/airports.csv` : distance, destination, récompense, heure de départ et météo varient à chaque recherche.
- Un seul contrat peut être accepté à la fois.
- Les pistes d'amélioration prévues sont listées dans [to_do.md](to_do.md).
