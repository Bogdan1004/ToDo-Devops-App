FROM python:3.11-slim

WORKDIR /app

# Copiere dependente mai intai (optimizare cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiere cod sursa
COPY app/ ./app/

EXPOSE 8000

# Parola NU e in cod! Vine din environment variables (Kubernetes Secrets)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]