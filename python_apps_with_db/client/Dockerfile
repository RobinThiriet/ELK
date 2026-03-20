FROM python:3.9-slim

WORKDIR /app

# Copier les dependances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code du client
COPY client.py .

# Le client doit connaitre l'adresse du serveur.
# On utilise une variable d'environnement par defaut, surchargee par docker compose.
ENV SERVER_URL=http://localhost:5000

# Lancer le client
CMD ["python", "client.py"]
