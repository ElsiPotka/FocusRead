#!/usr/bin/env bash
#
# First-time deployment script for FocusRead.
# 1. Starts services with HTTP-only nginx (for certbot challenge)
# 2. Obtains SSL certificate via certbot
# 3. Switches nginx to HTTPS config and reloads
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROD_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROD_DIR"

# ── Verify .env exists ──────────────────────────────────────────────
if [ ! -f .env ]; then
    echo "ERROR: .env file not found in $PROD_DIR"
    echo "Copy .env.example from apps/deployment and fill in your values."
    exit 1
fi

# shellcheck source=/dev/null
source .env

# ── Validate required vars ──────────────────────────────────────────
for var in DOMAIN EMAIL POSTGRES_PASSWORD REDIS_PASSWORD GRAFANA_ADMIN_USER GRAFANA_ADMIN_PASSWORD; do
    if [ -z "${!var:-}" ]; then
        echo "ERROR: $var is not set in .env"
        exit 1
    fi
done

echo "==> Deploying FocusRead to ${DOMAIN}"

# ── Step 1: Start with HTTP config ─────────────────────────────────
echo "==> Setting up HTTP-only nginx for certbot challenge..."
cp nginx/http.conf nginx/active.conf
sed -i "s/\${DOMAIN}/${DOMAIN}/g" nginx/active.conf

echo "==> Building and starting services..."
docker compose build
docker compose up -d

echo "==> Waiting for services to be ready..."
sleep 10

# ── Step 2: Run database migrations ────────────────────────────────
echo "==> Running database migrations..."
docker compose exec api alembic upgrade head

# ── Step 3: Obtain SSL certificate ──────────────────────────────────
echo "==> Requesting SSL certificate for ${DOMAIN}..."
docker compose run --rm certbot certonly \
    --webroot \
    -w /var/www/certbot \
    -d "${DOMAIN}" \
    --email "${EMAIL}" \
    --agree-tos \
    --no-eff-email

# ── Step 4: Switch to HTTPS config ──────────────────────────────────
echo "==> Switching nginx to HTTPS..."
cp nginx/https.conf nginx/active.conf
sed -i "s/\${DOMAIN}/${DOMAIN}/g" nginx/active.conf

docker compose exec nginx nginx -s reload
echo ""
echo "==> Deployment complete!"
echo "    API: https://${DOMAIN}/api/v1/health"
echo "    Docs: https://${DOMAIN}/docs"
echo "    Grafana: https://${DOMAIN}/grafana/"
echo "    Prometheus (server only): http://127.0.0.1:${PROMETHEUS_PORT:-9090}"
echo "    Loki (server only): http://127.0.0.1:${LOKI_PORT:-3100}/ready"
