# Consigne 5 - python_apps_with_db avec PostgreSQL et collecte ELK

Cette variante reprend le meme principe que les consignes precedentes :

- `server` et `client` ecrivent chacun leurs logs localement
- un `Filebeat` par service collecte ces logs
- les evenements partent vers la stack ELK principale
- le `server` utilise en plus une base PostgreSQL dediee

## Services

- `server`
- `client`
- `db`
- `filebeat-server`
- `filebeat-client`

## Lancement

```bash
cd /root/ELK/python_apps_with_db
docker compose up --build -d
```

## Logs produits

- `python_apps_with_db/runtime_logs/server/server.log`
- `python_apps_with_db/runtime_logs/client/client.log`

## Collecte

### Filebeat serveur

- configuration : `python_apps_with_db/filebeat/server-filebeat.yml`
- lit : `python_apps_with_db/runtime_logs/server/*.log`

### Filebeat client

- configuration : `python_apps_with_db/filebeat/client-filebeat.yml`
- lit : `python_apps_with_db/runtime_logs/client/*.log`

## Base de donnees

Le service `db` lance PostgreSQL avec :

- base : `observability`
- utilisateur : `observability`
- mot de passe : `observability`

Le serveur initialise automatiquement la table `lab_data` et injecte des donnees de test si besoin.

## Ce qu'il faut surveiller dans Kibana

```text
source_filename : "server.log"
```

```text
source_filename : "client.log"
```

```text
message : "*database*" or message : "*PostgreSQL*" or message : "*Fake query failed*"
```

```text
level : "ERROR" or level : "CRITICAL"
```

## Arret

```bash
docker compose down
```
