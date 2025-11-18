FROM python:3.11-slim

# dépendances système pour yt-dlp et ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY app/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app /app

ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/app

# dossier pour stocker les musiques
VOLUME /data/media

# dossier runtime (db etc.)
VOLUME /data/runtime

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
