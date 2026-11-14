#!/bin/sh
# Remet une sauvegarde dans le volume de données de {{NOM}}. Le service est arrêté pendant l'opération.
#   sh infra/restaurer.sh sauvegardes/donnees-AAAAMMJJ-HHMMSS.tar.gz
# Une sauvegarde jamais restaurée n'est pas une sauvegarde : tester ce script au moins une fois.
set -eu
ARCHIVE="${1:?Donner le chemin de l'archive à restaurer.}"
VOLUME="{{NOM_TECHNIQUE}}_donnees"
[ -f "$ARCHIVE" ] || { echo "Archive introuvable : $ARCHIVE"; exit 1; }
DOSSIER="$(cd "$(dirname "$ARCHIVE")" && pwd)"
FICHIER="$(basename "$ARCHIVE")"

printf 'Le volume %s va être remplacé par %s. Taper OUI : ' "$VOLUME" "$FICHIER"
read -r reponse
[ "$reponse" = "OUI" ] || { echo "Annulé."; exit 1; }

docker compose -f "$(dirname "$0")/docker-compose.yml" stop service
# Le service tourne sans root (utilisateur 1000) : les fichiers lui sont rendus après l'extraction.
docker run --rm --user root -v "$VOLUME":/donnees -v "$DOSSIER":/entree:ro alpine:3.22 sh -c "
  set -eu
  find /donnees -mindepth 1 -delete
  tar -xzf '/entree/$FICHIER' -C /donnees
  chown -R 1000:1000 /donnees
"
docker compose -f "$(dirname "$0")/docker-compose.yml" start service
echo "Restauration faite depuis $FICHIER."
