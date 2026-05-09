#!/usr/bin/env bash
# Daily Dish — local backpressure suite. Mirrors what CI runs, plus a couple of
# checks (codegen drift, Playwright smoke) that CI doesn't trigger on every job.
# Treat a non-zero exit as "not done": fix the failing step, then re-run.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# --- Pretty banners --------------------------------------------------------
if [[ -t 1 ]]; then
	BLUE=$'\033[1;36m'
	YELLOW=$'\033[33m'
	GREEN=$'\033[32m'
	RED=$'\033[1;31m'
	RESET=$'\033[0m'
else
	BLUE=""
	YELLOW=""
	GREEN=""
	RED=""
	RESET=""
fi

step() { printf '\n%s▶ %s%s\n' "$BLUE" "$1" "$RESET"; }
note() { printf '%s  %s%s\n' "$YELLOW" "$1" "$RESET"; }
ok()   { printf '%s  ✓ %s%s\n' "$GREEN" "$1" "$RESET"; }

trap 'printf "\n%s✘ verify failed%s\n" "$RED" "$RESET"' ERR

# --- API -------------------------------------------------------------------
step "API · ruff (lint + format)"
(cd apps/api && uv run ruff check app/ tests/ && uv run ruff format --check app/ tests/)

step "API · basedpyright"
(cd apps/api && uv run basedpyright)

step "API · pytest"
(cd apps/api && uv run pytest --tb=short)

step "API · alembic check"
# alembic env.py reads DATABASE_URL from os.environ, but unlike FastAPI it does
# *not* auto-load apps/api/.env. Source it here so a developer who has the API
# running (and therefore a working .env) doesn't get a confusing auth failure.
# If .env is missing, fall through and let alembic surface its own error.
if [[ -f apps/api/.env ]]; then
	set -a
	# shellcheck disable=SC1091
	source apps/api/.env
	set +a
fi
(cd apps/api && uv run alembic check)
ok "schema in sync with models"

# --- Web -------------------------------------------------------------------
step "Web · biome"
(cd apps/web && npm run lint)

step "Web · nuxi typecheck"
(cd apps/web && npm run typecheck)

step "Web · openapi codegen drift"
api_url="${NUXT_API_PROXY_TARGET:-http://localhost:8000}"
if curl -sf --max-time 2 "$api_url/openapi.json" -o /dev/null; then
	# Snapshot the on-disk types BEFORE regenerating, then compare. This asks
	# "is codegen output stable?" rather than "is the file committed?" — so a
	# developer who has correctly run codegen but not yet committed isn't
	# punished. Real drift (API shape changed without running codegen) still
	# trips the check.
	typed_path="apps/web/types/api.d.ts"
	snapshot="$(mktemp)"
	cp "$typed_path" "$snapshot"
	(cd apps/web && npm run codegen >/dev/null)
	drift=0
	diff -q "$snapshot" "$typed_path" >/dev/null || drift=1
	rm -f "$snapshot"
	if (( drift )); then
		printf '%s✘ apps/web/types/api.d.ts drifted after codegen.%s\n' "$RED" "$RESET"
		printf '   the regenerated file differs from what was on disk — re-run: npm --prefix apps/web run codegen\n'
		exit 1
	fi
	ok "no drift"
else
	note "API at $api_url unreachable — skipping codegen drift check"
fi

step "Web · vitest"
(cd apps/web && npm run test)

step "Web · playwright smoke"
# Playwright needs chromium installed AND the API reachable. Skip with a hint if
# either is missing rather than failing — these are heavier prerequisites that
# a quick pre-PR `verify` shouldn't punish you for forgetting.
playwright_cache="${PLAYWRIGHT_BROWSERS_PATH:-}"
if [[ -z "$playwright_cache" ]]; then
	if [[ -d "$HOME/Library/Caches/ms-playwright" ]] || [[ -d "$HOME/.cache/ms-playwright" ]]; then
		playwright_cache="present"
	fi
fi
if [[ -z "$playwright_cache" ]]; then
	note "chromium not installed — run \`cd apps/web && npx playwright install chromium\` to enable the smoke spec"
elif ! curl -sf --max-time 2 "$api_url/openapi.json" -o /dev/null; then
	note "API at $api_url unreachable — skipping Playwright smoke"
else
	(cd apps/web && npm run e2e)
fi

printf '\n%s✓ verify passed%s\n' "$GREEN" "$RESET"
