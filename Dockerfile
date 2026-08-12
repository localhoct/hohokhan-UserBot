FROM node:24-bookworm-slim AS node-runtime

FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data \
    TEMP_DIR=/tmp/hohokhan

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        ffmpeg \
        libzbar0 \
        libstdc++6 \
        tesseract-ocr \
        tesseract-ocr-eng \
        tesseract-ocr-fas \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# yt-dlp requires a modern JavaScript runtime for full YouTube support.
COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node

COPY requirements.txt ./
RUN pip install --requirement requirements.txt

COPY pyproject.toml README.md ./
COPY hohokhan ./hohokhan
COPY scripts ./scripts
RUN pip install --no-deps . \
    && addgroup --system --gid 10001 hohokhan \
    && adduser --system --uid 10001 --ingroup hohokhan --home /app hohokhan \
    && mkdir -p /app/data /tmp/hohokhan \
    && chown -R hohokhan:hohokhan /app /tmp/hohokhan

USER 10001:10001

CMD ["python", "-m", "hohokhan"]
