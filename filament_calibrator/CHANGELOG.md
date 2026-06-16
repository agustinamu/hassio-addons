# Changelog

## 0.1.0

- Versión inicial del addon: guía de calibración de filamentos en OrcaSlicer
  (Bambu Lab P1S) servida por ingress.
- Guía multi-material data-driven (PLA, PETG, TPU 90A).
- Calcula flow ratio, factor K (Pressure Advance, método Tower) y MVS.
- Persiste cada filamento en `/data` (sobrevive a reinicios y updates).
- Exporte opcional a Spoolman vía la opción `spoolman_url`.
