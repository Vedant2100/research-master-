FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends bash ca-certificates curl nodejs npm procps \
    && rm -rf /var/lib/apt/lists/*
COPY trustval.py /app/trustval.py
COPY request.json /app/request.json
RUN useradd --create-home --shell /bin/bash agent && chown -R root:root /app && chmod -R a-w /app
