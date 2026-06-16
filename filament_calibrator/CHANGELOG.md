# Changelog

## 0.1.1

- Fix ingress: el CSS/JS estático daba 404 bajo el ingress de HA (página sin estilos).
  La causa era fijar `scope["root_path"]` (clave reservada por Starlette para enrutar
  Mount), que rompía `StaticFiles`. Ahora se usa una clave propia `ingress_path`.
- Test de regresión: `/static` debe servirse con la cabecera `X-Ingress-Path`.

## 0.1.0

- Versión inicial del addon: guía de calibración de filamentos en OrcaSlicer
  (Bambu Lab P1S) servida por ingress.
- Guía multi-material data-driven (PLA, PETG, TPU 90A).
- Calcula flow ratio, factor K (Pressure Advance, método Tower) y MVS.
- Persiste cada filamento en `/data` (sobrevive a reinicios y updates).
- Exporte opcional a Spoolman vía la opción `spoolman_url`.
