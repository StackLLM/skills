#!/bin/sh
# Envoie vers main le dernier commit « livraison » de la recette, seulement si sa CI est verte.
set -eu
exec node "$(dirname "$0")/.github/livrer.mjs"
