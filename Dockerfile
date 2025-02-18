FROM python:3.11.1-slim

WORKDIR /app

RUN apt update && apt install -y restic && rm -rf /var/lib/apt/lists/*

COPY charon/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./charon ./charon
CMD ["python3", "-m", "charon", "-f", "/config/charon.yml"]

