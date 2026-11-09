FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN useradd --system ttt
USER ttt
EXPOSE 8000
# Tabellen aanmaken + startinhoud (alleen bij een lege database), daarna de API starten.
# Geen access log: we bewaren geen IP-adressen (zie privacybeleid).
CMD ["sh", "-c", "python -m app.cli init-db && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips='*' --no-access-log"]
