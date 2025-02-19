FROM python:3.13.2-slim

WORKDIR /app

RUN apt update && apt install -y restic rclone && rm -rf /var/lib/apt/lists/*

COPY charon/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./charon ./charon
CMD ["python3", "-m", "charon", "-f", "/config/charon.yml"]

