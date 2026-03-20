import time
import random
import logging
import threading
import sys
import os
from flask import Flask, request, jsonify
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.trace import SpanKind
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
import psycopg2
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

# -----------------
# CONFIGURATION DU TRACING
# -----------------
resource = Resource(attributes={"service.name": "api-server"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
span_processor = None
if otlp_endpoint:
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

# TracerProvider dedie a PostgreSQL pour distinguer la base dans les traces
db_resource = Resource(attributes={"service.name": "postgresql"})
db_provider = TracerProvider(resource=db_resource)
if span_processor:
    db_provider.add_span_processor(span_processor)

# Instrumentation Psycopg2 avec le provider dedie
# enable_commenter ajoute des commentaires SQL pour mieux lier les traces aux requetes
Psycopg2Instrumentor().instrument(tracer_provider=db_provider, enable_commenter=True)

# -----------------
# CONFIGURATION DES LOGS
# -----------------
class TraceInjectingFormatter(logging.Formatter):
    def format(self, record):
        span = trace.get_current_span()
        trace_id = span.get_span_context().trace_id
        if trace_id == 0:
            record.trace_id = "0"
            record.span_id = "0"
        else:
            record.trace_id = format(trace_id, "032x")
            record.span_id = format(span.get_span_context().span_id, "016x")
        return super().format(record)

log_formatter = TraceInjectingFormatter('%(asctime)s - %(name)s - %(levelname)s - [trace_id=%(trace_id)s span_id=%(span_id)s] - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)

LOG_DIR = os.getenv("LOG_DIR", "/app/logs")
os.makedirs(LOG_DIR, exist_ok=True)
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "server.log"))
file_handler.setFormatter(log_formatter)

logger = logging.getLogger("api-server")
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

# -----------------
# CONFIGURATION DES METRIQUES
# -----------------
# Expose automatiquement /metrics et suit les requetes HTTP.
metrics = PrometheusMetrics(app)

# Information statique exposee comme metrique
metrics.info('app_info', 'Application info', version='1.0.0')

def get_db_connection():
    """
    Retourne une connexion PostgreSQL a partir des variables d'environnement.
    """
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "postgres"),
        connect_timeout=5
    )

def init_db():
    """
    Initialise la base : attend la connexion, cree la table et injecte des donnees d'exemple.
    """
    logger.info("Initialisation de la connexion a la base et du schema...")
    max_retries = 10
    for i in range(max_retries):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            # Cree la table si elle n'existe pas
            cur.execute("CREATE TABLE IF NOT EXISTS lab_data (id SERIAL PRIMARY KEY, value INTEGER);")
            
            # Insere des donnees d'exemple si la table est vide
            cur.execute("SELECT COUNT(*) FROM lab_data;")
            if cur.fetchone()[0] == 0:
                logger.info("Base vide. Insertion des donnees de test.")
                sample_values = [1, 2, 3, 4, 5]
                for val in sample_values:
                    cur.execute("INSERT INTO lab_data (value) VALUES (%s);", (val,))
                conn.commit()
                logger.info("Donnees de test inserees avec succes.")
            
            cur.close()
            conn.close()
            logger.info("Initialisation de la base terminee.")
            return True
        except Exception as e:
            logger.warning(f"Echec de connexion a la base ({i+1}/{max_retries}) : {e}")
            time.sleep(3)
    
    logger.critical("Impossible de se connecter a la base apres plusieurs tentatives. Arret.")
    sys.exit(1)

def crash_simulator():
    """
    Thread de fond qui provoque aleatoirement des incidents sur le serveur.
    Cela simule des problemes comme une surcharge CPU, une fuite memoire
    ou un crash brutal, afin de travailler l'analyse de logs et de metriques.
    """
    logger.info("Simulateur de chaos initialise. Un incident surviendra plus tard.")
    # Attend entre 2 et 10 minutes avant de declencher un incident
    wait_time = random.randint(120, 600)
    time.sleep(wait_time)
    
    incidents = ['cpu_spike', 'memory_leak', 'sudden_crash']
    incident = random.choice(incidents)
    
    logger.critical(f"INCIDENT INITIATED: {incident.upper()} DETECTED!")
    
    if incident == 'cpu_spike':
        logger.error("SYSTEM ALERT: CPU load reaching 100%. System becoming unresponsive.")
        # Simule 100 % de CPU sur ce thread
        while True:
            pass
            
    elif incident == 'memory_leak':
        logger.error("SYSTEM ALERT: Out of memory. Rapid consumption detected.")
        leak_array = []
        try:
            while True:
                # Ajoute de gros blocs de texte pour saturer la memoire
                leak_array.append(" " * (10 ** 7)) # ~10 Mo par iteration
                time.sleep(0.05) # Monte vite en charge memoire
        except MemoryError:
            logger.critical("SYSTEM ALERT: MemoryError raised! Crashing process.")
            os._exit(1)
            
    elif incident == 'sudden_crash':
        logger.fatal("SYSTEM ALERT: Fatal Segmentation Fault or Kernel Panic. Process dying.")
        os._exit(1)

@app.route('/')
def index():
    logger.info("Acces a l'endpoint racine")
    return jsonify({"status": "running", "message": "Bienvenue sur l'API du laboratoire d'observabilite"})

@app.route('/data')
def get_data():
    logger.debug("Requete recue sur /data")
    
    # Simule une latence aleatoire
    if random.random() < 0.2:
        sleep_time = random.uniform(0.5, 3.0)
        logger.warning(f"Simulation de forte latence : la requete prendra {sleep_time:.2f}s")
        time.sleep(sleep_time)
        
    # Simule aleatoirement des erreurs 500 pour le TP
    if random.random() < 0.1:
        logger.error("Echec de lecture depuis la base. Simulation d'un timeout de connexion.")
        return jsonify({"error": "Echec de connexion a la base", "details": "Timeout"}), 500
        
    try:
        with tracer.start_as_current_span(
            "fetch-data-from-db", 
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.name": os.getenv("DB_NAME", "postgres"),
                "db.statement": "SELECT value FROM lab_data ORDER BY id;",
                "peer.service": "postgresql"
            }
        ):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT value FROM lab_data ORDER BY id;")
            rows = cur.fetchall()
            data = [row[0] for row in rows]
            cur.close()
            conn.close()
            
        logger.info(f"Lecture reussie de {len(data)} elements depuis PostgreSQL.")
        return jsonify({"data": data, "count": len(data)})
    except Exception as e:
        logger.error(f"Erreur inattendue pendant la requete PostgreSQL : {e}")
        return jsonify({"error": "Erreur interne du serveur", "details": str(e)}), 500

@app.route('/process', methods=['POST'])
def process_data():
    logger.debug("Requete POST recue sur /process")
    payload = request.json
    
    if not payload:
        logger.warning("Payload POST vide recu.")
        return jsonify({"error": "Aucun payload fourni"}), 400
        
    logger.info(f"Traitement d'un payload de taille {len(str(payload))}")
    time.sleep(random.uniform(0.1, 0.5)) # Petit temps de traitement
    
    # Fait echouer aleatoirement le traitement
    if random.random() < 0.05:
        logger.error("Echec du traitement a cause d'une erreur de validation interne.")
        return jsonify({"error": "Echec de validation du payload"}), 422
        
    logger.info("Traitement termine avec succes.")
    return jsonify({"status": "processed", "result": "success"})

@app.route('/fake')
def fake_query():
    logger.debug("Requete recue sur /fake")
    try:
        with tracer.start_as_current_span(
            "fake-failing-db-query", 
            kind=SpanKind.CLIENT,
            attributes={
                "db.system": "postgresql",
                "db.name": os.getenv("DB_NAME", "postgres"),
                "db.statement": "SELECT * FROM non_existent_table;",
                "peer.service": "postgresql"
            }
        ):
            conn = get_db_connection()
            cur = conn.cursor()
            # Cette requete echoue volontairement pour generer une erreur PostgreSQL
            cur.execute("SELECT * FROM non_existent_table;")
            cur.fetchall()
            cur.close()
            conn.close()
    except Exception as e:
        logger.error(f"Erreur base volontaire declenchee sur /fake : {e}")
        return jsonify({"error": "Echec volontaire de la requete fictive", "details": str(e)}), 500
        
    return jsonify({"warning": "Cette requete n'aurait pas du reussir"}), 200

if __name__ == '__main__':
    # Initialise la base avant le demarrage du serveur

    init_db()
    
    # Lance le simulateur de chaos en arriere-plan
    threading.Thread(target=crash_simulator, daemon=True).start()
    
    logger.info("Demarrage de l'application Flask d'observabilite sur le port 5000")
    app.run(host='0.0.0.0', port=5000)
