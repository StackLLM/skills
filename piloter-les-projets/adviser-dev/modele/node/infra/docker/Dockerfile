# {{NOM}} : un seul service Node pour l'API et le frontend compilé.
# Construire depuis la racine du projet : docker build -f infra/docker/Dockerfile .
# Le code vit dans l'image. Les données vivent sur le volume /donnees : une nouvelle image ne les touche pas.

# ---- Étape 1 : compiler le frontend ----
FROM node:24.14.0-bookworm-slim AS compilation
WORKDIR /app
# Les dépendances d'abord : elles ne se réinstallent que si un package.json change.
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/
COPY backend/package.json backend/
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build -w frontend

# ---- Étape 2 : l'image qui tourne ----
FROM node:24.14.0-bookworm-slim
ENV NODE_ENV=production
WORKDIR /app
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/
COPY backend/package.json backend/
# Node lit le TypeScript directement : pas besoin des outils de développement.
RUN npm ci --omit=dev --no-audit --no-fund && npm cache clean --force
COPY backend/src backend/src
COPY --from=compilation /app/frontend/dist frontend/dist

# Sans droits root : le service n'écrit que dans /donnees.
RUN mkdir -p /donnees && chown node:node /donnees
USER node

ENV {{PREFIXE}}_PORT={{PORT}} \
    {{PREFIXE}}_HOTE=0.0.0.0 \
    {{PREFIXE}}_DONNEES=/donnees

VOLUME /donnees
EXPOSE {{PORT}}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD node -e "fetch('http://127.0.0.1:{{PORT}}/sante/vivant').then(r => process.exit(r.ok ? 0 : 1), () => process.exit(1))"

CMD ["node", "backend/src/index.ts"]
