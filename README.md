# Consigne 3 - Un Filebeat par service

Cette branche est dediee a une variante plus proche d'un cas reel :

- le `server` ecrit ses logs dans son propre dossier
- le `client` ecrit ses logs dans son propre dossier
- chaque service a son propre `Filebeat`
- les deux `Filebeat` envoient ensuite les logs a `Logstash`
- `Logstash` alimente `Elasticsearch`
- `Kibana` sert a l'analyse

Cette branche ne remplace pas les autres :

- `main` : branche de reference
- `consigne-1-log-analysed` : logs statiques dans `log_analysed/`
- `consigne-2-python-apps-filebeat` : logs dynamiques centralises dans un dossier partage
- `consigne-3-filebeat-par-service` : logs dynamiques avec un collecteur par service

## Architecture

```mermaid
flowchart LR
    U[Utilisateur] -->|API| API[API Flask<br/>localhost:8000]
    U -->|Navigateur| K[Kibana<br/>localhost:5601]

    subgraph APPS[python_apps]
        S[server]
        C[client]
        SL[python_apps/runtime_logs/server/server.log]
        CL[python_apps/runtime_logs/client/client.log]
        FBS[Filebeat server]
        FBC[Filebeat client]

        S --> SL
        C --> CL
        SL --> FBS
        CL --> FBC
    end

    subgraph ELK[Stack ELK]
        L[Logstash<br/>5044]
        E[Elasticsearch<br/>9200]
        K
    end

    C -->|HTTP| S
    FBS -->|Beats| L
    FBC -->|Beats| L
    L --> E
    E --> K
```

## Principe

Ici, on evite le dossier central `log_analysed/python_apps/`.

A la place :

- `server` ecrit dans `python_apps/runtime_logs/server/`
- `client` ecrit dans `python_apps/runtime_logs/client/`
- `filebeat-server` lit uniquement les logs du serveur
- `filebeat-client` lit uniquement les logs du client

Ce modele ressemble davantage a un environnement reel ou chaque machine ou service collecte ses propres logs localement avant de les envoyer a la plateforme d'observabilite.

## Contenu de la branche

```text
.
├── docker-compose.yml
├── logstash/
│   └── pipeline/
│       └── logstash.conf
├── python_apps/
│   ├── docker-compose.yml
│   ├── filebeat/
│   │   ├── server-filebeat.yml
│   │   └── client-filebeat.yml
│   ├── runtime_logs/
│   │   ├── server/
│   │   └── client/
│   ├── server/
│   ├── client/
│   └── README_fr-FR.md
└── README.md
```

## Prerequis

- Docker
- Docker Compose via `docker compose`

## Ports

- `8000` : API Flask exposee localement
- `9200` : Elasticsearch
- `5601` : Kibana
- `5044` : entree Beats de Logstash
- `5000` : entree TCP JSON optionnelle de Logstash

## Demarrage

### 1. Demarrer ELK

```bash
cd /root/ELK
docker compose up -d
```

### 2. Demarrer l'application et les collecteurs

```bash
cd /root/ELK/python_apps
docker compose up --build -d
```

## Fonctionnement

1. `server` ecrit `server.log` dans `python_apps/runtime_logs/server/`
2. `client` ecrit `client.log` dans `python_apps/runtime_logs/client/`
3. `filebeat-server` lit uniquement `/srv/logs/*.log` monte depuis `runtime_logs/server/`
4. `filebeat-client` lit uniquement `/srv/logs/*.log` monte depuis `runtime_logs/client/`
5. les deux envoient vers `logstash:5044`
6. `Logstash` parse les lignes et enrichit les evenements
7. `Elasticsearch` les indexe
8. `Kibana` permet de les rechercher

## Avantages de cette approche

- separation claire entre les sources de logs
- plus proche d'un deploiement reel
- plus simple a raisonner quand on ajoute d'autres services
- chaque collecteur peut etre configure independamment

## Verification

### API

```text
http://localhost:8000
```

### Kibana

```text
http://localhost:5601
```

Dans `Discover`, utilise la Data View `demo`, puis filtre par exemple :

```text
source_filename : "server.log"
```

```text
source_filename : "client.log"
```

```text
level : "ERROR" or level : "CRITICAL"
```

```text
event_type : "chaos_incident" or event_type : "system_alert"
```

```text
event_type : "client_connection_failed" or event_type : "client_timeout"
```

## Reconstruction rapide

### Tout lancer

```bash
cd /root/ELK
docker compose up -d

cd /root/ELK/python_apps
docker compose up --build -d
```

### Tout arreter

```bash
cd /root/ELK/python_apps
docker compose down

cd /root/ELK
docker compose down
```

### Repartir proprement

```bash
cd /root/ELK/python_apps
docker compose down

cd /root/ELK
docker compose down
docker compose up -d

cd /root/ELK/python_apps
docker compose up --build -d
```

## Fichiers importants

- [docker-compose.yml](/root/ELK/docker-compose.yml)
- [logstash.conf](/root/ELK/logstash/pipeline/logstash.conf)
- [python_apps/docker-compose.yml](/root/ELK/python_apps/docker-compose.yml)
- [server-filebeat.yml](/root/ELK/python_apps/filebeat/server-filebeat.yml)
- [client-filebeat.yml](/root/ELK/python_apps/filebeat/client-filebeat.yml)
- [README_fr-FR.md](/root/ELK/python_apps/README_fr-FR.md)
