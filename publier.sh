#!/usr/bin/env bash
# Publie les changements du dépôt et met à jour les plugins installés.
#
# Usage :
#   ./publier.sh "message du commit"
#
# 1. Valide le marketplace et chaque plugin.
# 2. Committe tout, puis pousse sur chaque URL de push d'origin
#    (StackLLM/skills et la copie personnelle, si elle est configurée).
# 3. Met à jour le marketplace stackllm-skills et chaque plugin installé.
#
# Sans changement à committer, il saute l'étape 2 et met quand même à jour.

set -euo pipefail

DEPOT="$(cd "$(dirname "$0")" && pwd)"
cd "$DEPOT"

echo "== Validation"
claude plugin validate . >/dev/null
python3 - <<'EOF' | while read -r source; do claude plugin validate "$source" >/dev/null; done
import json
for p in json.load(open(".claude-plugin/marketplace.json"))["plugins"]:
    print(p["source"])
EOF
echo "ok"

if [ -n "$(git status --porcelain)" ]; then
  message="${1:-}"
  if [ -z "$message" ]; then
    echo "Des fichiers ont changé : donner un message de commit." >&2
    echo "  ./publier.sh \"message\"" >&2
    exit 1
  fi
  echo "== Commit et push"
  git add -A
  git commit -q -m "$message"
  git push -q origin HEAD
  git remote get-url --push --all origin | sed 's/^/poussé → /'
else
  echo "== Rien à committer"
  git push -q origin HEAD
fi

echo "== Mise à jour des plugins"
claude plugin marketplace update stackllm-skills >/dev/null
claude plugin list 2>/dev/null \
  | sed -n 's/.*❯ \([^ ]*@stackllm-skills\).*/\1/p' \
  | while read -r plugin; do
      claude plugin update "$plugin" 2>&1 | tail -n 1
    done
echo "Fait. Les nouvelles versions prennent effet à la prochaine session."
