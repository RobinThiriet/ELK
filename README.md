# ELK - Guide principal

Ce depot regroupe cinq consignes progressives autour d'une stack d'observabilite locale basee sur `Elasticsearch`, `Logstash`, `Kibana`, `Filebeat`, `Jaeger` et des applications Python de demonstration.

L'objectif du `main` est simple :

- centraliser les commandes `make`
- servir de point d'entree pour toutes les consignes
- documenter clairement comment lancer, stopper et nettoyer l'environnement

## Consignes disponibles

| Consigne | Branche | Objectif principal |
| --- | --- | --- |
| 1 | `consigne-1-log-analysed` | analyser des logs statiques deja presents |
| 2 | `consigne-2-python-apps-filebeat` | collecter des logs dynamiques avec une application Python |
| 3 | `consigne-3-filebeat-par-service` | separer les logs du client et du serveur avec un Filebeat par service |
| 4 | `consigne-4-jaeger-ui` | ajouter Jaeger UI et le tracing distribue client / serveur |
| 5 | `consigne-5-python-apps-with-db` | ajouter PostgreSQL et une variante `python_apps_with_db` |

## Prerequis

- Docker
- Docker Compose disponible via `docker compose`
- `make`

Verification rapide :

```bash
docker --version
docker compose version
make --version
```

## Commandes Make

Toutes les commandes se lancent depuis la racine du projet :

```bash
cd /root/ELK
```

### Aide

```bash
make help
```

### Lancer la branche active

```bash
make up
```

Ou, de maniere equivalente :

```bash
make all
```

Comportement :

- sur `main`, la commande lance la stack ELK de reference
- sur une branche de consigne, la commande lance la stack correspondant a cette branche

### Basculer et lancer directement une consigne

```bash
make consigne1
make consigne2
make consigne3
make consigne4
make consigne5
```

Chaque cible :

- bascule automatiquement sur la bonne branche Git
- demarre les services necessaires
- prepare l'environnement de logs associe si besoin

### Voir l'etat courant

```bash
make status
```

La commande affiche :

- la branche Git active
- l'etat des conteneurs ELK
- l'etat de `python_apps` si present
- l'etat de `python_apps_with_db` si present

### Voir la branche courante

```bash
make branch
```

### Arreter proprement l'environnement

```bash
make clean
```

Ou :

```bash
make clean-all
```

La commande :

- arrete `python_apps` si la variante est presente
- arrete `python_apps_with_db` si la variante est presente
- arrete la stack ELK
- supprime les conteneurs et les reseaux dedies

### Nettoyer completement

```bash
make prune
```

La commande :

- execute d'abord `make clean`
- supprime les volumes Docker dedies au projet
- supprime les logs locaux generes par les applications

## Flux de travail recommande

### Lancer une consigne precise

```bash
make consigne4
```

### Verifier l'etat

```bash
make status
```

### Arreter sans perdre les volumes

```bash
make clean
```

### Repartir de zero

```bash
make prune
```

## Points d'acces

Selon la consigne active, les services suivants peuvent etre disponibles :

- `http://localhost:5601` : Kibana
- `http://localhost:9200` : Elasticsearch
- `http://localhost:8000` : API Flask
- `http://localhost:16686` : Jaeger UI

## Documentation par branche

Chaque branche contient son propre `README.md` avec :

- le contexte de la consigne
- l'architecture associee
- les commandes de lancement et d'arret
- les points de verification dans Kibana ou Jaeger

## Fichiers importants

- [Makefile](/root/ELK/Makefile)
- [scripts/infra.sh](/root/ELK/scripts/infra.sh)
- [docker-compose.yml](/root/ELK/docker-compose.yml)
- [logstash/pipeline/logstash.conf](/root/ELK/logstash/pipeline/logstash.conf)
