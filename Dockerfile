FROM python:3.11-slim

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

# create and set permissions for runtime volumes
RUN mkdir -p /srv/apps/radiocolloc/media /srv/apps/radiocolloc/runtime \
    && chmod -R 775 /srv/apps/radiocolloc

VOLUME ["/srv/apps/radiocolloc/media", "/srv/apps/radiocolloc/runtime"]

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
