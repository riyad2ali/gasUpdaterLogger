FROM python:3.12-slim

# PYTHONUNBUFFERED so `docker logs` shows output in real time.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config.yaml ./

RUN mkdir -p /app/data

CMD ["python", "src/main.py"]
