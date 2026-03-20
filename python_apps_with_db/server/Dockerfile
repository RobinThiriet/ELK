FROM python:3.9-slim

WORKDIR /app

# Copier les dependances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code du serveur
COPY server.py .

# Exposer le port Flask
EXPOSE 5000

# Lancer le serveur
CMD ["python", "server.py"]
