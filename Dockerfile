FROM python:3.11.1-slim

WORKDIR /app

COPY charon/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./charon .
CMD ["python3", "charon.py", "-f", "/config/charon.yml"]

