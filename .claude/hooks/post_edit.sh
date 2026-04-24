#!/usr/bin/env bash
# Backpressure: after Claude edits a file, run the right formatter/linter on it.
# - apps/api/*.py       → ruff check --fix, ruff format
# - apps/web/{ts,vue,…} → biome check --write
# Exit 2 on unfixable errors so the message flows back into Claude's context.

set -u

payload=$(cat)
file=$(printf '%s' "$payload" | python3 -c 'import json,sys; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("file_path",""))' 2>/dev/null || echo "")

[ -z "$file" ] && exit 0
[ ! -f "$file" ] && exit 0

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
rel="${file#"$repo_root"/}"

case "$rel" in
  *node_modules/*|*/.nuxt/*|*/.venv/*|*/__pycache__/*|apps/web/types/api.d.ts) exit 0 ;;
esac

if [[ "$rel" == apps/api/*.py ]]; then
  rel_in_api="${rel#apps/api/}"
  cd "$repo_root/apps/api" || exit 0
  uv run --quiet ruff check --fix "$rel_in_api" 1>&2 || exit 2
  uv run --quiet ruff format "$rel_in_api" 1>&2 || exit 2
  exit 0
fi

if [[ "$rel" == apps/web/* ]]; then
  case "$rel" in
    *.ts|*.tsx|*.vue|*.js|*.mjs|*.mts|*.cts|*.json|*.jsonc)
      rel_in_web="${rel#apps/web/}"
      cd "$repo_root/apps/web" || exit 0
      npx --no-install biome check --write "$rel_in_web" 1>&2 || exit 2
      ;;
  esac
fi

exit 0
