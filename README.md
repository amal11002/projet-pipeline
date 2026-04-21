#  Pipeline d'analyse de données météo en temps réel

Projet réalisé dans le cadre du cours **8CLD876 — Conception et architecture des systèmes d'infonuagique**.

```

## Structure du projet

```
projet-pipeline/
├── docker-compose.yml       # Orchestration de tous les services
├── producer/                # Bloc A — Producteur de données
│   ├── producer.py          # Appelle OpenWeatherMap et envoie dans Kafka
│   ├── requirements.txt
│   ├── .env                 # Clé API (ne pas committer !)
│   └── Dockerfile
├── processor/               # Bloc B — Traitement Spark
│   ├── processor.py         # Spark Structured Streaming + écriture PostgreSQL
│   └── Dockerfile
├── dashboard/               # Bloc C — Dashboard Streamlit
│   ├── app.py               # Dashboard temps réel (localhost:8501)
│   ├── requirements.txt
│   └── Dockerfile
├── scripts_sql/
│   └── init.sql             # Création de la table weather_processed
└── README.md
```

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) — doit être lancé avant toute commande docker
- [Python 3.11+](https://www.python.org/)
- Une clé API gratuite sur [openweathermap.org](https://openweathermap.org/api)

---

## Démarrage rapide

### 1. Cloner le repo

```bash
git clone https://github.com/amal11002/projet-pipeline
cd projet-pipeline
```

### 2. Configurer la clé API

Créer un fichier `.env` dans le dossier `producer/` :

```
API_KEY=ta_clé_openweathermap
```

> Clé gratuite sur [openweathermap.org](https://openweathermap.org/api) — active en ~10 minutes après inscription.

### 3. Lancer l'infrastructure

```bash
docker compose up -d --build
```

Vérifier que les 5 services sont **Up** :

```bash
docker compose ps
```


### 4. Lancer le producteur

Dans un **deuxième terminal** :

```bash
cd producer
pip install -r requirements.txt
python producer.py
```

Résultat attendu :

```
Producteur démarré — envoi vers le topic 'weather_data' toutes les 30s
Envoyé : {'city': 'Montreal', 'temperature': 2.52, 'humidity': 30.0, ...}
Envoyé : {'city': 'Quebec City', 'temperature': -0.88, 'humidity': 39.0, ...}
Envoyé : {'city': 'Toronto', 'temperature': 3.13, 'humidity': 33.0, ...}
```

### 5. Ouvrir le dashboard

Attendre 1-2 minutes, puis ouvrir dans le navigateur :

```
http://localhost:8501
```

---

## Bloc A — Producteur de données

Le producteur est un script Python qui interroge l'API OpenWeatherMap toutes les 30 secondes pour 3 villes canadiennes (Montréal, Québec, Toronto) et envoie les données en JSON dans le topic Kafka `weather_data`.

**Données envoyées pour chaque ville :**
- Température (°C)
- Humidité (%)
- Timestamp
---

## Bloc B — Traitement Spark Structured Streaming

Spark consomme le topic Kafka `weather_data`, calcule une moyenne de température par ville et détecte les anomalies (écart > 5°C), puis écrit les résultats dans la table PostgreSQL `weather_processed`.

**Pour tester :**

```bash
git fetch origin
git checkout processor
```

Vérifier les données dans PostgreSQL :

```bash
docker exec -it postgres psql -U user -d weather -c "SELECT * FROM weather_processed ORDER BY timestamp DESC LIMIT 10;"
```

Résultat attendu :

```
     city     |      timestamp      |      avg_temp       | is_anomaly
--------------+---------------------+---------------------+------------
 Toronto      | 2026-04-21 01:24:27 |   3.130000114440918 | f
 Quebec City  | 2026-04-21 01:24:26 | -0.8799999952316284 | f
 Montreal     | 2026-04-21 01:24:26 |  2.5199999809265137 | f
```

---

## Bloc C — Dashboard Streamlit

Le dashboard se connecte à PostgreSQL et affiche en temps réel :
- Courbe de température par ville
- Indicateurs de dernières valeurs
- Alertes en rouge si anomalie détectée
- Tableau de l'historique des 100 dernières mesures

Accessible sur : **http://localhost:8501** — rafraîchissement automatique toutes les 10s.



## Branches

| Branche | Contenu | Responsable |
|---|---|---|
| `main` | Infrastructure Docker + README | Amal |
| `producer` | Bloc A — Producteur Kafka | Amal |
| `processor` | Bloc B — Traitement Spark | Coéquipier 2 |
| `dashboard` | Bloc C — Dashboard Streamlit | Coéquipier 3 |

---

## Technologies utilisées

| Technologie | Rôle |
|---|---|
| Apache Kafka | Streaming des messages météo |
| Apache Spark Structured Streaming | Traitement temps réel, détection d'anomalies |
| PostgreSQL | Stockage de l'historique |
| Streamlit + Plotly | Dashboard interactif |
| Docker Compose | Orchestration de tous les services |
| OpenWeatherMap API | Source de données météo |