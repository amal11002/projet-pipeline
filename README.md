# Pipeline d'analyse de données météo en temps réel

Projet réalisé dans le cadre du cours **8CLD876 — Conception et architecture des systèmes d'infonuagique**.

## Structure du projet

```
projet-pipeline/
├── docker-compose.yml       # Orchestration de tous les services
├── producer/                # Bloc A — Producteur de données
│   ├── producer.py          # Script Python qui envoie les données dans Kafka
│   ├── Dockerfile
│   └── requirements.txt
├── processor/               # Bloc B — Traitement Spark
│   ├── processor.py         # Spark Structured Streaming + écriture PostgreSQL
│   └── Dockerfile
├── dashboard/               # Bloc C — Dashboard Streamlit
│   ├── app.py               # Dashboard Streamlit temps réel
│   └── Dockerfile
└── README.md
```

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python 3.11+](https://www.python.org/)
- Une clé API gratuite sur [openweathermap.org](https://openweathermap.org/api)

---

## Démarrage rapide

### 1. Cloner le repo

```bash
git clone https://github.com/amal11002/projet-pipeline
cd projet-pipeline
```

### 2. Lancer l'infrastructure (Kafka + PostgreSQL)

```bash
docker compose up -d
```

Vérifier que les 3 services tournent :

```bash
docker compose ps
```

---

## Bloc A

Le producteur est un script Python qui interroge l'API OpenWeatherMap toutes les 30 secondes pour 3 villes canadiennes (Montréal, Québec, Toronto) et envoie les données en JSON dans le topic Kafka `weather_data`.

**Données envoyées pour chaque ville :**
- Température (°C)
- Humidité (%)
- Vitesse du vent (m/s)
- Description météo (ex: broken clouds)
- Timestamp

### Tester le Bloc A

**1. Récupérer la branche**

```bash
git fetch origin
git checkout producer
```

**2. Créer le fichier `.env` dans le dossier `producer/`**

```
API_KEY=ta_clé_openweathermap
```

> Clé gratuite disponible sur [openweathermap.org](https://openweathermap.org/api) — active en ~10 minutes après inscription.

**3. Installer les dépendances**

```bash
cd producer
pip install -r requirements.txt
```

**4. Lancer le producteur**

```bash
python producer.py
```

**Résultat attendu :**

```
Producteur démarré — envoi vers le topic 'weather_data' toutes les 30s
Envoyé : {'city': 'Montreal', 'temp': 5.74, 'humidity': 57, 'wind': 5.66, ...}
Envoyé : {'city': 'Quebec City', 'temp': 2.83, 'humidity': 75, 'wind': 4.02, ...}
Envoyé : {'city': 'Toronto', 'temp': 4.08, 'humidity': 75, 'wind': 6.17, ...}
```

> Le script tourne en continu. `Ctrl+C` pour arrêter.

## Bloc B

Le Bloc B correspond au traitement temps réel des données reçues depuis Kafka avec **Spark Structured Streaming**, puis à leur écriture dans PostgreSQL.

### Tester les Blocs A et B

Pour tester correctement le traitement du Bloc B, il faut utiliser la branche **`test-processor`**, car elle contient les ajustements permettant de valider l’enchaînement entre :
- le **Bloc A** : envoi des données météo dans Kafka
- le **Bloc B** : lecture des messages Kafka, traitement Spark et écriture en base PostgreSQL

**1. Récupérer la branche de test**

```bash
git fetch origin
git checkout test-processor
```

**2. Lancer l'infrastructure**

Depuis la racine du projet :

```bash
docker compose up -d --build
```

**3. Vérifier que les conteneurs tournent**

```bash
docker compose ps
```

**4. Lancer le producer pour alimenter Kafka**

Dans un autre terminal :

```bash
cd producer
python producer.py
```

**5. Vérifier les logs du processor**

```bash
docker logs -f weather_processor
```

**6. Vérifier l'écriture en base PostgreSQL**

```bash
docker exec -it postgres psql -U user -d weather -c "SELECT * FROM weather_processed ORDER BY timestamp DESC LIMIT 10;"
```

**Résultat attendu :**

Le processor doit rester actif, consommer les messages du topic Kafka `weather_data`, puis écrire des lignes dans la table `weather_processed`.

Exemple de résultat attendu dans PostgreSQL :

```text
    city     |      timestamp      |      avg_temp      | is_anomaly
-------------+---------------------+--------------------+------------
 Quebec City | 2026-04-20 20:06:27 | 2.0899999141693115 | f
 Toronto     | 2026-04-20 20:06:27 | 5.710000038146973  | f
 Montreal    | 2026-04-20 20:06:26 | 5.090000152587891  | f
```

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