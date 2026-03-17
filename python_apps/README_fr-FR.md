# Consigne 2 - Application Python a observer avec ELK

Ce dossier contient l'application utilisee pour la `consigne 2`.

But :

- lancer un serveur Flask instable
- lancer un client qui genere du trafic
- produire des logs dynamiques
- envoyer ces logs vers la stack ELK principale grace a `Filebeat`

## Composants

- `server` : API Flask instable avec simulateur de chaos
- `client` : trafic HTTP continu vers le serveur

## Lancement

Depuis ce dossier :

```bash
cd /root/ELK/python_apps
docker compose up --build -d
```

## Services exposes

- API Flask : `http://localhost:8000`
- endpoint metriques : `http://localhost:8000/metrics`

## Dossier de logs

Les logs sont ecrits sur l'hote dans :

```text
../log_analysed/python_apps/
```

Fichiers attendus :

- `server.log`
- `client.log`

## Integration avec ELK

Le flux retenu est le suivant :

```text
server/client
  -> fichiers .log
  -> Filebeat
  -> Logstash
  -> Elasticsearch
  -> Kibana
```

## Ce qu'il faut surveiller

Dans `server.log` :

- activite normale de l'API
- `ERROR`
- `CRITICAL`
- `INCIDENT INITIATED`
- `SYSTEM ALERT`

Dans `client.log` :

- succes HTTP
- erreurs HTTP
- `TIMEOUT`
- `CONNECTION FAILED`

## Symptomes possibles

Le simulateur de chaos peut provoquer :

- un pic CPU
- une fuite memoire
- un crash brutal

## Utilisation dans Kibana

Filtres KQL utiles :

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
