# ELK avec Docker Compose

Ce projet fournit une stack **ELK** simple à démarrer en local avec Docker Compose.

- **Elasticsearch** stocke et indexe les données
- **Logstash** reçoit et transforme les logs
- **Kibana** permet de rechercher et visualiser les événements

L'objectif est d'avoir un environnement prêt pour apprendre ELK, faire des tests locaux, ou démarrer une petite démo rapidement.

## Architecture

Le projet démarre 3 conteneurs :

- `elasticsearch` sur le port `9200`
- `logstash` sur les ports `5000` et `5044`
- `kibana` sur le port `5601`

Flux principal :

1. Tu ajoutes des logs dans le dossier `logs/`
2. Logstash lit les fichiers `.log`
3. Logstash envoie les événements dans Elasticsearch
4. Kibana affiche les données stockées

## Structure du projet

```text
.
├── docker-compose.yml
├── logstash
│   └── pipeline
│       └── logstash.conf
├── logs
│   └── app.log
└── README.md
```

## Prérequis

- Docker installé
- Docker Compose disponible via `docker compose`
- Au moins 4 Go de RAM alloués à Docker

Vérification rapide :

```bash
docker --version
docker compose version
```

## Fichiers importants

### `docker-compose.yml`

Déclare les 3 services ELK :

- Elasticsearch en mode `single-node`
- Logstash avec la pipeline montée depuis le dossier local
- Kibana connecté à Elasticsearch

### `logstash/pipeline/logstash.conf`

Cette pipeline :

- lit tous les fichiers `*.log` du dossier `/var/log/demo`
- écoute aussi sur le port TCP `5000` au format JSON
- envoie tout dans l'index `logs-demo-YYYY.MM.dd`

### `logs/app.log`

Fichier d'exemple pour tester immédiatement l'ingestion.

## Démarrage du projet

Place-toi dans le dossier du projet :

```bash
cd /root/ELK
```

Démarre la stack :

```bash
docker compose up -d
```

Vérifie l'état des conteneurs :

```bash
docker compose ps
```

Consulte les logs si besoin :

```bash
docker compose logs -f
```

## Vérifier que tout fonctionne

### Elasticsearch

Ouvre dans ton navigateur :

```text
http://localhost:9200
```

Ou teste dans le terminal :

```bash
curl http://localhost:9200
```

Si tout va bien, tu verras un JSON avec le nom du nœud, la version et le cluster.

### Kibana

Ouvre :

```text
http://localhost:5601
```

Kibana peut mettre 30 à 90 secondes à être complètement prêt après le démarrage.

### Logstash

Important : `http://localhost:5000` ne doit pas être ouvert dans un navigateur.

Le port `5000` n'est pas une interface web. C'est une **entrée TCP** utilisée par Logstash pour recevoir des événements JSON.

## Comment utiliser la stack

### Cas 1. Lire un fichier de logs

Le dossier local `./logs` est monté dans le conteneur Logstash.

Tous les fichiers avec l'extension `.log` sont lus automatiquement.

Exemple :

```bash
echo "2026-03-16 10:15:00 INFO Nouveau log" >> logs/app.log
```

Autres exemples :

```bash
echo "2026-03-16 10:15:05 WARN Cache miss user=42" >> logs/app.log
echo "2026-03-16 10:15:10 ERROR Payment service unavailable" >> logs/app.log
```

Ces événements seront envoyés dans Elasticsearch dans un index de type :

```text
logs-demo-2026.03.16
```

### Cas 2. Envoyer un événement JSON à Logstash

Tu peux aussi injecter des événements en direct via le port TCP `5000`.

Exemple :

```bash
printf '{"service":"api","level":"info","message":"hello from tcp"}\n' | nc localhost 5000
```

Autre exemple :

```bash
printf '{"service":"billing","level":"error","message":"payment failed","user_id":42}\n' | nc localhost 5000
```

## Afficher les logs dans Kibana

Une fois Kibana disponible :

1. Ouvre `http://localhost:5601`
2. Va dans `Stack Management`
3. Ouvre `Data Views`
4. Clique sur `Create data view`
5. Saisis le pattern :

```text
logs-demo-*
```

6. Choisis `@timestamp` comme champ temporel si Kibana le propose
7. Ouvre ensuite `Discover`

Tu verras les événements ingérés par Logstash.

## Scénario de test complet

Voici un test simple du début à la fin :

1. Démarrer la stack

```bash
docker compose up -d
```

2. Ajouter un log

```bash
echo "2026-03-16 11:00:00 INFO test elk" >> logs/app.log
```

3. Ouvrir Kibana

```text
http://localhost:5601
```

4. Créer la data view `logs-demo-*`

5. Aller dans `Discover` et rafraîchir

Tu devrais alors voir le log apparaître.

## Commandes utiles

Démarrer :

```bash
docker compose up -d
```

Arrêter :

```bash
docker compose down
```

Supprimer aussi les volumes :

```bash
docker compose down -v
```

Voir les logs des conteneurs :

```bash
docker compose logs -f
```

Redémarrer la stack :

```bash
docker compose restart
```

Reconstruire proprement :

```bash
docker compose down -v
docker compose up -d
```

## Dépannage

### Kibana ne s'ouvre pas

Attends un peu après le `docker compose up -d`, puis vérifie :

```bash
docker compose ps
docker compose logs kibana
```

### Elasticsearch répond mais pas Kibana

C'est fréquent au démarrage. Elasticsearch est souvent prêt avant Kibana.

### `localhost:5000` ne montre rien dans le navigateur

C'est normal.

Le port `5000` n'est pas un site web. Il sert uniquement à recevoir des données TCP pour Logstash.

### Les nouveaux logs n'apparaissent pas

Vérifie :

```bash
docker compose logs logstash
```

Puis ajoute une nouvelle ligne dans `logs/app.log` :

```bash
echo "2026-03-16 12:00:00 INFO verification logstash" >> logs/app.log
```

### Plus assez de mémoire

Si Docker manque de RAM, Elasticsearch ou Kibana peuvent démarrer lentement ou planter.

Dans ce cas, augmente la mémoire allouée à Docker Desktop ou ajuste les options Java dans `docker-compose.yml`.

## Limites de cette configuration

Cette stack est pensée pour le local et la démonstration.

- la sécurité Elasticsearch est désactivée
- il n'y a pas d'authentification
- il n'y a pas de persistance avancée ni de tuning production

Pour un usage de production, il faut ajouter :

- sécurité et gestion des mots de passe
- certificats TLS
- monitoring
- sauvegardes
- réglages mémoire et disque

## Résumé

Pour utiliser ce projet :

1. lance `docker compose up -d`
2. ouvre `http://localhost:5601`
3. crée la data view `logs-demo-*`
4. ajoute des logs dans `logs/app.log`
5. consulte-les dans `Discover`
