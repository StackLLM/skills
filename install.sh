#!/usr/bin/env bash
# Installe les Skills de ce dépôt dans ~/.claude/skills par liens symboliques.
#
# Usage :
#   ./install.sh                 toutes les Skills
#   ./install.sh cloneme cv-ats  seulement celles-ci (nom déclaré dans SKILL.md)
#
# Un dossier existant qui n'est pas un lien vers ce dépôt n'est jamais remplacé.

set -euo pipefail

DEPOT="$(cd "$(dirname "$0")" && pwd)"
CIBLE="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
mkdir -p "$CIBLE"

for skill_md in "$DEPOT"/*/*/SKILL.md; do
  dossier="$(dirname "$skill_md")"
  nom="$(sed -n 's/^name:[[:space:]]*//p' "$skill_md" | head -n 1)"
  [ -n "$nom" ] || continue

  if [ "$#" -gt 0 ] && [[ " $* " != *" $nom "* ]]; then
    continue
  fi

  lien="$CIBLE/$nom"
  if [ -e "$lien" ] && [ ! -L "$lien" ]; then
    echo "ignoré   $nom : $lien existe déjà et n'est pas un lien"
    continue
  fi

  ln -sfn "$dossier" "$lien"
  echo "installé $nom → ${dossier#"$DEPOT"/}"
done
