# Changelog

## 0.27.1

- Versión inicial del addon sobre Homebox 0.27.1 (imagen oficial `ghcr.io/sysadminsmedia/homebox`).
- Opciones `hostname`, `allow_registration` y `trust_proxy` mapeadas a `HBOX_OPTIONS_*`.
- `api_key_pepper` (obligatorio desde 0.27) generado en el primer arranque y guardado en `/data`.
- Puerto 7745 sin ingress (los QR se abren fuera de la app de HA), healthcheck heredado y backup en frío.
