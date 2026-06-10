# Stage 1: Build Next.js frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .

# Same-origin API calls through nginx in the unified container.
# Force empty at build time so Railway service variables cannot bake localhost into the bundle.
ENV DOCKER_BUILD=true
RUN NEXT_PUBLIC_API_URL= npm run build

# Stage 2: Node 20 runtime binaries (matches frontend build)
FROM node:20-bookworm-slim AS node-runtime

# Stage 3: Unified runtime (FastAPI + Next.js + nginx)
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libmagic1 \
    ffmpeg \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY --from=node-runtime /usr/local/bin/node /usr/local/bin/node
COPY --from=node-runtime /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/bin/node /usr/local/bin/nodejs

# Backend
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt
# Warm Presidio/spaCy so the first verify request does not download models at runtime
RUN python -c "import spacy; spacy.load('en_core_web_sm')"
COPY backend/app ./backend/app

# Frontend (Next.js standalone)
COPY --from=frontend-builder /frontend/public ./frontend/public
COPY --from=frontend-builder /frontend/.next/standalone ./frontend
COPY --from=frontend-builder /frontend/.next/static ./frontend/.next/static

# Process orchestration
COPY docker/nginx.conf.template /etc/nginx/nginx.conf.template
COPY docker/start.sh /start.sh
RUN sed -i 's/\r$//' /start.sh && chmod +x /start.sh

ENV PORT=8080
ENV INTERNAL_API_URL=http://127.0.0.1:8000
ENV PYTHONPATH=/app/backend

EXPOSE 8080

CMD ["/start.sh"]
