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

## Tableau recapitulatif

| Consigne | Commande | Commande d'arret | Ce que ca lance | Ports utiles | Verification recommandee |
| --- | --- | --- | --- | --- | --- |
| 1 | `make consigne1` | `make clean1` | ELK + ingestion de logs statiques | `5601`, `9200` | ouvrir Kibana et verifier les index `elk-demo-*` |
| 2 | `make consigne2` | `make clean2` | ELK + `python_apps` + Filebeat partage | `8000`, `5601`, `9200` | verifier `server.log` et `client.log` dans Kibana |
| 3 | `make consigne3` | `make clean3` | ELK + `python_apps` + un Filebeat par service | `8000`, `5601`, `9200` | verifier la separation des logs client / serveur |
| 4 | `make consigne4` | `make clean4` | ELK + `python_apps` + Jaeger UI | `8000`, `5601`, `9200`, `16686` | verifier les logs dans Kibana et les traces dans Jaeger |
| 5 | `make consigne5` | `make clean5` | ELK + `python_apps_with_db` + PostgreSQL | `8000`, `5601`, `9200`, `16686` | verifier `api-client-db`, `api-server-db` et les logs lies a PostgreSQL |

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

Important :

- le projet se pilote uniquement depuis `/root/ELK`
- apres `make consigneX`, le depot reste sur la branche de la consigne lancee
- pour revenir sur la documentation globale, il faut repasser sur `main`

```bash
git checkout main
```

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
make clean1
make clean2
make clean3
make clean4
make clean5
make clean-all
```

Commandes disponibles :

- `make clean1` arrete ce que `make consigne1` a lance
- `make clean2` arrete ce que `make consigne2` a lance
- `make clean3` arrete ce que `make consigne3` a lance
- `make clean4` arrete ce que `make consigne4` a lance
- `make clean5` arrete ce que `make consigne5` a lance
- `make clean-all` arrete toutes les stacks du projet
- `make clean` reste un alias de `make clean-all`

### Nettoyer completement

```bash
make prune
```

La commande :

- execute d'abord `make clean`
- supprime les volumes Docker dedies au projet
- supprime les logs locaux generes par les applications

## Exemples rapides

### Consigne 1

```bash
make consigne1
make clean1
```

### Consigne 2

```bash
make consigne2
make clean2
```

### Consigne 3

```bash
make consigne3
make clean3
```

### Consigne 4

```bash
make consigne4
make clean4
```

### Consigne 5

```bash
make consigne5
make clean5
```

### Tout arreter

```bash
make clean-all
```

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
