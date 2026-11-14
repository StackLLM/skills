# {{NOM}} : le backend FastAPI, qui sert aussi le frontend compilé.
# Construire depuis la racine du projet : docker build -f infra/docker/Dockerfile .
# Le code vit dans l'image. Les données vivent sur le volume /donnees : une nouvelle image ne les touche pas.

# ---- Étape 1 : compiler le frontend ----
FROM node:24.14.0-bookworm-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/
RUN npm ci --no-audit --no-fund
COPY frontend frontend
RUN npm run build -w frontend

# ---- Étape 2 : installer le backend ----
FROM python:3.13-slim AS backend
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/app/.venv
WORKDIR /app/backend
# Les dépendances d'abord : elles ne se réinstallent que si pyproject.toml ou uv.lock change.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev

# ---- Étape 3 : l'image qui tourne ----
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH"
WORKDIR /app/backend
# Sans droits root : un utilisateur dédié (uid 1000), qui n'écrit que dans /donnees.
RUN useradd --uid 1000 --create-home service && mkdir -p /donnees && chown service:service /donnees
COPY --from=backend /app/.venv /app/.venv
COPY backend/app app
COPY --from=frontend /app/frontend/dist /app/frontend/dist
USER service

ENV {{PREFIXE}}_ENVIRONNEMENT=production \
    {{PREFIXE}}_PORT={{PORT}} \
    {{PREFIXE}}_HOTE=0.0.0.0 \
    {{PREFIXE}}_DONNEES=/donnees \
    {{PREFIXE}}_SITE=/app/frontend/dist

VOLUME /donnees
EXPOSE {{PORT}}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:{{PORT}}/sante/vivant', timeout=4).status == 200 else 1)"

# uvicorn s'arrête proprement sur SIGTERM (requêtes en cours finies, 10 s max). Pas de --proxy-headers :
# l'application lit X-Forwarded-For elle-même, seulement si {{PREFIXE}}_PROXY=1. Pas de journal d'accès
# d'uvicorn : l'application écrit déjà une ligne structurée par requête.
CMD ["sh", "-c", "exec uvicorn app.main:application --host \"${{PREFIXE}}_HOTE\" --port \"${{PREFIXE}}_PORT\" --timeout-graceful-shutdown 10 --no-server-header --no-access-log"]
