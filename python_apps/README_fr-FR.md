# Consigne 4 - python_apps avec Filebeat par service et Jaeger UI

Ce dossier contient la variante la plus proche d'un cas reel pour le TP.

Principe :

- le `server` ecrit ses logs dans son propre dossier
- le `client` ecrit ses logs dans son propre dossier
- `filebeat-server` collecte uniquement les logs du serveur
- `filebeat-client` collecte uniquement les logs du client
- les deux envoient les evenements vers la stack ELK principale
- les deux exportent aussi leurs traces distribuees vers `Jaeger`

## Services

- `server`
- `client`
- `filebeat-server`
- `filebeat-client`
- `Jaeger` dans la stack racine pour la visualisation des traces

## Lancement

```bash
cd /root/ELK/python_apps
docker compose up --build -d
```

## Logs produits

- `python_apps/runtime_logs/server/server.log`
- `python_apps/runtime_logs/client/client.log`

## Collecte

### Filebeat serveur

- configuration : `python_apps/filebeat/server-filebeat.yml`
- lit : `python_apps/runtime_logs/server/*.log`

### Filebeat client

- configuration : `python_apps/filebeat/client-filebeat.yml`
- lit : `python_apps/runtime_logs/client/*.log`

## Destination

Les deux collecteurs envoient vers :

```text
logstash:5044
```

sur le reseau partage `elk-observability`.

Pour le tracing, `server` et `client` exportent leurs spans vers :

```text
jaeger:4317
```

et l'interface est disponible sur :

```text
http://localhost:16686
```

## Pourquoi cette approche

- on se rapproche d'un fonctionnement reel
- chaque service garde ses logs localement
- chaque source a son propre collecteur
- on peut faire evoluer les deux collecteurs separement
- on visualise aussi les traces distribuees entre le client et le serveur

## Ce qu'il faut surveiller dans Kibana

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

## Arret

```bash
docker compose down
```
