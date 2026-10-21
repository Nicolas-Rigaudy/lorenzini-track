#!/usr/bin/env bash
# Run the backend tests against a fresh, disposable PostGIS and MQTT broker.
# Usage: backend/scripts/test.sh [pytest args...]
set -euo pipefail

backend_dir="$(cd "$(dirname "$0")/.." && pwd)"
compose=(docker compose -f "$backend_dir/../docker-compose.yml" --profile test)

cleanup() { "${compose[@]}" rm --stop --force db-test mqtt-test >/dev/null 2>&1 || true; }
trap cleanup EXIT

cleanup
"${compose[@]}" up --detach --wait db-test mqtt-test

cd "$backend_dir"
export DATABASE_URL="postgresql+psycopg://test:test@localhost:5433/test"
export MQTT_HOST=localhost MQTT_PORT=1884
python=python
[[ -x .venv/bin/python ]] && python=.venv/bin/python
"$python" -m pytest "$@"
