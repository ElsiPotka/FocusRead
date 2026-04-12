#!/usr/bin/env bash
#
# Rebuild and restart one or more containers after code changes.
#
# Usage:
#   ./redeploy.sh              # redeploys api + worker (default)
#   ./redeploy.sh api          # redeploys only api
#   ./redeploy.sh worker       # redeploys only worker
#   ./redeploy.sh api worker   # redeploys api and worker
#   ./redeploy.sh --migrate    # redeploys api + worker and runs migrations
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROD_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROD_DIR"

RUN_MIGRATE=false
SERVICES=()

for arg in "$@"; do
    if [ "$arg" = "--migrate" ]; then
        RUN_MIGRATE=true
    else
        SERVICES+=("$arg")
    fi
done

# Default to api + worker if no services specified
if [ ${#SERVICES[@]} -eq 0 ]; then
    SERVICES=("api" "worker")
fi

echo "==> Redeploying: ${SERVICES[*]}"

# ── Rebuild ─────────────────────────────────────────────────────────
echo "==> Building images..."
docker compose build "${SERVICES[@]}"

# ── Restart with zero-downtime for api ──────────────────────────────
for svc in "${SERVICES[@]}"; do
    echo "==> Restarting ${svc}..."
    docker compose up -d --no-deps "${svc}"
done

# ── Run migrations if requested ─────────────────────────────────────
if [ "$RUN_MIGRATE" = true ]; then
    echo "==> Running database migrations..."
    docker compose exec api alembic upgrade head
fi

# ── Show status ─────────────────────────────────────────────────────
echo ""
echo "==> Current status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}"

echo ""
echo "==> Redeploy complete"
