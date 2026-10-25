#!/bin/sh
# Arranque del addon: mapea opciones de HA (/data/options.json) a env y lanza Homebox.
set -eu

OPTIONS=/data/options.json

# Nombres según backend/internal/sys/config/conf.go (prefijo HBOX, campo de Options).
HBOX_OPTIONS_HOSTNAME="$(jq -r '.hostname // ""' "${OPTIONS}")"
HBOX_OPTIONS_ALLOW_REGISTRATION="$(jq -r '.allow_registration' "${OPTIONS}")"
HBOX_OPTIONS_TRUST_PROXY="$(jq -r '.trust_proxy' "${OPTIONS}")"
HBOX_OPTIONS_GITHUB_RELEASE_CHECK=false
export HBOX_OPTIONS_HOSTNAME HBOX_OPTIONS_ALLOW_REGISTRATION HBOX_OPTIONS_TRUST_PROXY \
  HBOX_OPTIONS_GITHUB_RELEASE_CHECK

echo "[homebox] hostname='${HBOX_OPTIONS_HOSTNAME}' registro=${HBOX_OPTIONS_ALLOW_REGISTRATION} trust_proxy=${HBOX_OPTIONS_TRUST_PROXY}"

# Secreto obligatorio desde 0.27: se genera una vez y persiste en /data.
# Regenerarlo invalida las API keys emitidas.
PEPPER=/data/.api_key_pepper
if [ ! -s "${PEPPER}" ]; then
  (umask 077 && head -c 48 /dev/urandom | base64 | tr -d '\n' > "${PEPPER}")
fi
HBOX_AUTH_API_KEY_PEPPER="$(cat "${PEPPER}")"
export HBOX_AUTH_API_KEY_PEPPER

# BD y fotos en /data (variables ya fijadas en la imagen oficial).
exec /app/api /data/config.yml
