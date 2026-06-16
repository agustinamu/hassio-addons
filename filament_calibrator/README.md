# Filament Calibrator

Guía interactiva para calibrar filamentos en **OrcaSlicer** con una **Bambu Lab
P1S** (LAN-only, sin AMS, bobina externa, extrusor direct drive) y persistir los
resultados por filamento.

Forma parte de `filament-lab` (pieza 3.A). No sustituye a OrcaSlicer: Orca sigue
siendo la fuente de verdad del perfil. Esta app **guía** el proceso (en el orden
correcto), **calcula** los valores a partir de lo que observas en los tests y
**registra** un resumen por filamento.

## Qué hace (v1)

- Guía paso a paso multi-material: **PLA, PETG, TPU 90A** (añadir más = un YAML).
- Calcula flow ratio, factor K (Pressure Advance, método Tower), MVS.
- Persiste cada filamento en JSON local (`data/filaments/`).

El contenido de calibración vive en `content/materials/*.yaml` y *es* la
documentación; ver `content/SCHEMA.md`.

## Uso (desarrollo local con uv)

```bash
uv sync                                   # crea .venv e instala deps
uv run uvicorn app.main:app --reload      # http://127.0.0.1:8000
uv run pytest                             # tests
```

## Arquitectura

```
app/
  main.py          rutas FastAPI
  models.py        modelos Pydantic (contenido + registro)
  content.py       carga/valida los YAML de materiales
  calc.py          fórmulas de calibración
  storage/         persistencia (local JSON en v1; Spoolman después)
content/materials/ un YAML por material
data/filaments/    resultados (JSON, no versionado)
```

## Spoolman (opcional)

Si defines `CALIBRATOR_SPOOLMAN_URL`, aparece el botón **"Enviar a Spoolman"** en
la ficha, que exporta el filamento calibrado al inventario (a nivel *Filament*,
con sus custom fields: factor K, flow, MVS, retracción, perfil Orca…).

```bash
CALIBRATOR_SPOOLMAN_URL=http://<IP_HA>:7912 uv run uvicorn app.main:app --reload
```

`app/spoolman.py` define los custom fields, empareja por `calibrator_slug`
(idempotente) y hace read-merge-write del `extra`. **Validado contra la instancia real.**

## Addon de Home Assistant

Empaquetado como addon en esta misma carpeta (`config.yaml`, `Dockerfile` con uv que
reutiliza `pyproject.toml`/`uv.lock`, `build.yaml`, `run.sh`, `DOCS.md`). Sirve la UI por
**ingress** y persiste en `/data/filaments` (`CALIBRATOR_DATA_DIR=/data`). La opción
`spoolman_url` del addon mapea a `CALIBRATOR_SPOOLMAN_URL`. Instalación y opciones en
`DOCS.md`. Para probarlo en local: copiar la carpeta a `/addons/filament_calibrator/`.

## Llevar la calibración a otro equipo

No hay utilidad de backup de la carpeta de Orca: el resumen calibrado vive en **Spoolman**
(server-side, lo ven todos los PCs) y cada ficha incluye un bloque "Llevar a otro
OrcaSlicer" con el perfil base a duplicar y los valores a aplicar. El factor K viaja por la
propia impresora. Un backup de los `.json` de Orca solo haría falta si se tuneara el perfil
más allá de lo que calibra esta app; queda pendiente para cuando exista un segundo PC.
