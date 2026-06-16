# Filament Calibrator

Guía interactiva para calibrar filamentos en **OrcaSlicer** con una **Bambu Lab P1S**
(LAN-only, sin AMS, bobina externa, direct drive) y persistir el resultado por filamento.
Opcionalmente exporta el filamento calibrado a **Spoolman**.

No sustituye a OrcaSlicer: Orca sigue siendo la fuente de verdad del perfil. La app
**guía** el proceso, **calcula** los valores a partir de lo que observas en los tests y
**registra** un resumen por filamento.

## Instalación

### Como addon local (para probar)

1. Copia la carpeta del calibrador a `/addons/filament_calibrator/` de tu Home Assistant
   (vía Samba/SSH/File editor). Debe contener `config.yaml`, `Dockerfile`, `build.yaml`,
   `run.sh`, `app/`, `content/`, `pyproject.toml` y `uv.lock`.
2. **Ajustes → Add-ons → Add-on Store → ⋮ → Check for updates**. Aparece en
   *Local add-ons*.
3. Instala, configura la opción `spoolman_url` (opcional) y arranca.

### Desde un repositorio de addons

Añade el repositorio en **Add-on Store → ⋮ → Repositories** y aparecerá en la lista.

## Configuración

| Opción | Descripción |
|--------|-------------|
| `spoolman_url` | URL base de Spoolman (p.ej. `https://spoolman.midominio.com` o `http://<IP>:7912`). **Vacío = sin Spoolman**: el botón "Enviar a Spoolman" no aparece. No incluyas `/api/v1`. |

## Datos

Los filamentos se guardan en `/data/filaments/*.json`, que es **persistente**: sobreviven a
reinicios y actualizaciones del addon.

## Uso

Abre el addon (botón **Open Web UI** / barra lateral). Crea un filamento, recorre los pasos
guiados y, si tienes Spoolman configurado, expórtalo con "Enviar a Spoolman".

El factor K (PA) no se escribe en el perfil de Orca: vive en la impresora. El bloque
"Llevar a otro OrcaSlicer" de cada ficha resume los valores a aplicar en otro PC.
