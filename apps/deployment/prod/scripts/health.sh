#!/usr/bin/env bash
#
# Health check script — checks all FocusRead services.
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROD_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROD_DIR"

# shellcheck source=/dev/null
[ -f .env ] && source .env

DOMAIN="${DOMAIN:-localhost}"
PROTOCOL="https"
if [ "$DOMAIN" = "localhost" ]; then
    PROTOCOL="http"
fi

echo "==> FocusRead Health Check"
echo ""

# ── Docker containers ───────────────────────────────────────────────
echo "── Container Status ──"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""

# ── API health endpoint ────────────────────────────────────────────
echo "── API Health ──"
HEALTH_URL="${PROTOCOL}://${DOMAIN}/api/v1/health"
HTTP_CODE=$(curl -s -o /tmp/focusread_health.json -w "%{http_code}" --max-time 10 "$HEALTH_URL" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo "  Status: OK (HTTP $HTTP_CODE)"
    cat /tmp/focusread_health.json | python3 -m json.tool 2>/dev/null || cat /tmp/focusread_health.json
else
    echo "  Status: FAILED (HTTP $HTTP_CODE)"
    [ -f /tmp/focusread_health.json ] && cat /tmp/focusread_health.json
fi
echo ""

# ── Database ────────────────────────────────────────────────────────
echo "── Database ──"
if docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-focusread}" -q 2>/dev/null; then
    echo "  PostgreSQL: OK"
else
    echo "  PostgreSQL: UNREACHABLE"
fi

# ── PgBouncer (prod only) ──────────────────────────────────────────
if docker compose ps pgbouncer --format "{{.Name}}" 2>/dev/null | grep -q pgbouncer; then
    echo "── PgBouncer ──"
    if docker compose exec -T pgbouncer pg_isready -h 127.0.0.1 -p 6432 -q 2>/dev/null; then
        echo "  PgBouncer: OK"
    else
        echo "  PgBouncer: UNREACHABLE"
    fi
fi

# ── Redis ───────────────────────────────────────────────────────────
echo "── Redis ──"
REDIS_ARGS=""
if [ -n "${REDIS_PASSWORD:-}" ]; then
    REDIS_ARGS="-a ${REDIS_PASSWORD}"
fi
if docker compose exec -T redis redis-cli $REDIS_ARGS ping 2>/dev/null | grep -q PONG; then
    echo "  Redis: OK"
else
    echo "  Redis: UNREACHABLE"
fi
echo ""

# ── Grafana ─────────────────────────────────────────────────────────
if docker compose ps grafana --format "{{.Name}}" 2>/dev/null | grep -q grafana; then
    echo "── Grafana ──"
    GRAFANA_URL="${PROTOCOL}://${DOMAIN}/grafana/api/health"
    GRAFANA_CODE=$(curl -s -o /tmp/focusread_grafana_health.json -w "%{http_code}" --max-time 10 "$GRAFANA_URL" 2>/dev/null || echo "000")

    if [ "$GRAFANA_CODE" = "200" ]; then
        echo "  Grafana: OK (HTTP $GRAFANA_CODE)"
    else
        echo "  Grafana: FAILED (HTTP $GRAFANA_CODE)"
        [ -f /tmp/focusread_grafana_health.json ] && cat /tmp/focusread_grafana_health.json
    fi
    echo ""
fi

# ── Prometheus ──────────────────────────────────────────────────────
if docker compose ps prometheus --format "{{.Name}}" 2>/dev/null | grep -q prometheus; then
    echo "── Prometheus ──"
    PROM_URL="http://127.0.0.1:${PROMETHEUS_PORT:-9090}/-/ready"
    PROM_CODE=$(curl -s -o /tmp/focusread_prometheus_health.txt -w "%{http_code}" --max-time 10 "$PROM_URL" 2>/dev/null || echo "000")

    if [ "$PROM_CODE" = "200" ]; then
        echo "  Prometheus: OK (HTTP $PROM_CODE)"
    else
        echo "  Prometheus: FAILED (HTTP $PROM_CODE)"
        [ -f /tmp/focusread_prometheus_health.txt ] && cat /tmp/focusread_prometheus_health.txt
    fi
    echo ""
fi

# ── Loki ────────────────────────────────────────────────────────────
if docker compose ps loki --format "{{.Name}}" 2>/dev/null | grep -q loki; then
    echo "── Loki ──"
    LOKI_URL="http://127.0.0.1:${LOKI_PORT:-3100}/ready"
    LOKI_CODE=$(curl -s -o /tmp/focusread_loki_health.txt -w "%{http_code}" --max-time 10 "$LOKI_URL" 2>/dev/null || echo "000")

    if [ "$LOKI_CODE" = "200" ]; then
        echo "  Loki: OK (HTTP $LOKI_CODE)"
    else
        echo "  Loki: FAILED (HTTP $LOKI_CODE)"
        [ -f /tmp/focusread_loki_health.txt ] && cat /tmp/focusread_loki_health.txt
    fi
    echo ""
fi

# ── SSL certificate ────────────────────────────────────────────────
if [ "$PROTOCOL" = "https" ]; then
    echo "── SSL Certificate ──"
    EXPIRY=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN":443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ -n "$EXPIRY" ]; then
        echo "  Expires: $EXPIRY"
    else
        echo "  Could not check certificate"
    fi
fi

echo ""
echo "==> Done"
