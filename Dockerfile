FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Store the database at /data/bot.db.
# Mount a persistent volume there so it survives redeploys:
#   - docker-compose: already configured (see docker-compose.yml)
#   - Railway: add a Railway Volume in the dashboard, mount path /data
#   - Render: uses render.yaml's disk mounted at /var/data instead
ENV DB_PATH=/data/bot.db

CMD ["python", "bot.py"]
