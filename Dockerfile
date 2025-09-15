FROM python:3.13.2-slim

WORKDIR /app

RUN apt update && apt install -y tree sqlite3 jq curl bzip2 rclone && rm -rf /var/lib/apt/lists/*

ARG RESTIC_VERSION=0.18.0
RUN curl -L -o /tmp/restic.bz2 https://github.com/restic/restic/releases/download/v${RESTIC_VERSION}/restic_${RESTIC_VERSION}_linux_amd64.bz2 \
    && bunzip2 /tmp/restic.bz2 \
    && mv /tmp/restic /usr/local/bin/restic \
    && chmod +x /usr/local/bin/restic


COPY ./charon ./charon
COPY pyproject.toml README.md LICENSE .
RUN python3 -m pip install .
CMD ["charon", "-f", "/config/charon.yml"]

