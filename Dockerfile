FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Store the database at /data/bot.db.
# Mount a Railway Volume at /data in the dashboard so it survives redeploys.
ENV DB_PATH=/data/bot.db

CMD ["python", "bot.py"]
