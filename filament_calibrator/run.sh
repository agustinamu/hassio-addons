#!/usr/bin/env bash
# Arranque del addon: mapea opciones de HA (/data/options.json) a env y lanza uvicorn.
set -euo pipefail

# /data es persistente en addons de HA; los filamentos van en /data/filaments.
export CALIBRATOR_DATA_DIR=/data

OPTIONS=/data/options.json
if [ -f "${OPTIONS}" ]; then
  URL="$(python3 -c "import json; print(json.load(open('${OPTIONS}')).get('spoolman_url') or '')" 2>/dev/null || true)"
  if [ -n "${URL}" ]; then
    export CALIBRATOR_SPOOLMAN_URL="${URL}"
    echo "[calibrator] Spoolman: ${URL}"
  else
    echo "[calibrator] Spoolman no configurado (opción spoolman_url vacía)"
  fi
fi

# Puerto = ingress_port de config.yaml. --forwarded-allow-ips confía en el proxy de HA.
exec /opt/venv/bin/uvicorn app.main:app \
  --host 0.0.0.0 --port 8099 --forwarded-allow-ips '*'
