# Simple Python image with no extra deps
FROM python:3.11-slim

WORKDIR /app
COPY . /app

# No dependencies to install, but keep step for extensibility
RUN pip install --no-cache-dir -r requirements.txt || true

ENV PYTHONUNBUFFERED=1

CMD ["python", "app/service.py"]
