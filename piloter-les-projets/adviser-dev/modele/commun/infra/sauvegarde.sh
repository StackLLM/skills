#!/bin/sh
# Sauvegarde le volume de données de {{NOM}} dans une archive datée, et garde les 14 dernières.
#   sh infra/sauvegarde.sh [dossier-des-sauvegardes]
# À lancer chaque nuit (cron). Les archives doivent aussi partir hors de la machine.
set -eu
VOLUME="{{NOM_TECHNIQUE}}_donnees"
DOSSIER="${1:-./sauvegardes}"
GARDER=14
mkdir -p "$DOSSIER"
DOSSIER="$(cd "$DOSSIER" && pwd)"
NOM="donnees-$(date -u +%Y%m%d-%H%M%S).tar.gz"

# Les bases SQLite sont d'abord copiées de façon cohérente (VACUUM INTO) : une copie brute
# pendant que le service écrit peut donner une base abîmée.
docker run --rm --user root -v "$VOLUME":/donnees -v "$DOSSIER":/sortie python:3.13-alpine sh -c '
  set -eu
  mkdir -p /tmp/copie
  cp -a /donnees/. /tmp/copie/
  find /tmp/copie -name "*.sqlite-wal" -delete -o -name "*.sqlite-shm" -delete
  for base in $(cd /donnees && find . -name "*.sqlite"); do
    rm -f "/tmp/copie/$base"
    python3 -c "import sqlite3,sys; sqlite3.connect(sys.argv[1]).execute(\"VACUUM INTO ?\", (sys.argv[2],))" "/donnees/$base" "/tmp/copie/$base"
  done
  tar -czf "/sortie/'"$NOM"'" -C /tmp/copie .
'
echo "Sauvegarde : $DOSSIER/$NOM"

# Rotation : on garde les $GARDER plus récentes.
ls -1t "$DOSSIER"/donnees-*.tar.gz | tail -n +$((GARDER + 1)) | xargs -r rm -f
