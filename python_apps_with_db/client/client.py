import requests
import time
import random
import logging
import sys
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace.status import Status, StatusCode

# -----------------
# CONFIGURATION DU TRACING
# -----------------
resource = Resource(attributes={"service.name": "api-client"})
trace.set_tracer_provider(TracerProvider(resource=resource))
tracer = trace.get_tracer(__name__)

otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)

# Instrumente automatiquement `requests` pour propager `traceparent`
RequestsInstrumentor().instrument()

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
file_handler = logging.FileHandler(os.path.join(LOG_DIR, "client.log"))
file_handler.setFormatter(log_formatter)

logger = logging.getLogger("api-client")
logger.setLevel(logging.DEBUG)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:5000")

def run_client():
    logger.info(f"Demarrage du client API. Envoi continu de requetes vers {SERVER_URL}")
    request_interval = 1.0
    
    while True:
        try:
            # Choisit aleatoirement un endpoint pour generer du trafic
            endpoint = random.choices(
                ['/', '/data', '/process', '/fake'], 
                weights=[0.1, 0.6, 0.2, 0.1]
            )[0]
            
            with tracer.start_as_current_span("client_request") as span:
                span.set_attribute("http.url", endpoint)
                span.set_attribute("app.target", "api-server")
                span.set_attribute("app.request_interval_seconds", request_interval)
                logger.debug(f"Attempting to request {endpoint}")
                start_time = time.time()

                if endpoint == '/process':
                    payload = {"key": "observability_test", "id": random.randint(1, 10000)}
                    response = requests.post(f"{SERVER_URL}{endpoint}", json=payload, timeout=5)
                else:
                    response = requests.get(f"{SERVER_URL}{endpoint}", timeout=5)

                elapsed = time.time() - start_time
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.target", endpoint)
                span.set_attribute("app.response_latency_seconds", elapsed)

                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Journalise selon le code HTTP pour produire des logs utiles
                if response.status_code == 200:
                    logger.info(f"SUCCES (200 OK) | Endpoint: {endpoint} | Latence: {elapsed:.2f}s")
                elif response.status_code >= 500:
                    logger.error(f"ERREUR SERVEUR ({response.status_code}) | Endpoint: {endpoint} | Reponse: {response.text}")
                elif response.status_code >= 400:
                    logger.warning(f"ERREUR CLIENT ({response.status_code}) | Endpoint: {endpoint} | Reponse: {response.text}")
                else:
                    logger.info(f"STATUT INATTENDU ({response.status_code}) | Endpoint: {endpoint}")
                
        except requests.exceptions.Timeout:
            logger.error(f"TIMEOUT : la requete vers {SERVER_URL}{endpoint} a expire !")
        except requests.exceptions.ConnectionError:
            logger.critical(f"ECHEC DE CONNEXION : impossible de joindre le serveur a l'adresse {SERVER_URL}.")
        except Exception as e:
            logger.error(f"EXCEPTION INATTENDUE : {e}")
            
        # Fait varier la charge dans le temps
        if random.random() < 0.05:
            # Fait varier l'intervalle entre 0.1 (forte charge) et 3.0 (faible charge)
            request_interval = random.uniform(0.1, 3.0)
            logger.debug(f"Ajustement de l'intervalle de requete a {request_interval:.2f} seconde(s)")
            
        time.sleep(request_interval)

if __name__ == '__main__':
    run_client()
