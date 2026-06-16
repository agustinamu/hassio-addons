# Formato del contenido de calibración (YAML por material)

Cada archivo `materials/<code>.yaml` define un material y su proceso de
calibración. La app no conoce los materiales; solo este esquema. Añadir un
material nuevo (ABS, ASA, fibra…) = añadir un YAML; no hay que tocar código.

Validado por `app/models.py` (Pydantic). Si un YAML no valida, la app falla al
arrancar indicando el archivo culpable.

## Material

| Campo | Tipo | Notas |
|-------|------|-------|
| `code` | str | Identificador único (`pla`, `petg`, `tpu90a`). |
| `name` | str | Nombre legible. |
| `defaults` | objeto | Ver abajo. |
| `steps` | lista | Pasos ordenados de calibración. |

### `defaults`

| Campo | Tipo | Notas |
|-------|------|-------|
| `density` | float | g/cm³. |
| `diameter` | float | mm (1.75 normalmente). |
| `nozzle_range` | [int, int] | Rango orientativo de temperatura de nozzle. |
| `bed_range` | [int, int] | Rango orientativo de temperatura de cama. |
| `base_profile` | str | Perfil de Orca del que partir (se duplica y se renombra antes de calibrar). |
| `bed_temp` | int | Temperatura de cama fijada por material (no se calibra con test). |
| `retraction_speed` | int | Velocidad de retracción recomendada (mm/s). |

## Step

| Campo | Tipo | Notas |
|-------|------|-------|
| `id` | str | Único dentro del material. Convención: `temperature`, `flow_pass1`, `flow_pass2`, `pressure_advance`, `retraction`, `mvs`. |
| `title` | str | Título mostrado. |
| `optional` | bool | Por defecto `false`. En TPU, `pressure_advance` y `mvs` son `true`. |
| `ask_current` | bool | Por defecto `false`. Si `true`, el paso pide además el valor actual del perfil (base del cálculo), p.ej. el flow ratio de partida en el paso de flow YOLO. |
| `orca_path` | str | Ruta del menú de OrcaSlicer para lanzar el test. |
| `orca_apply` | str | Dónde meter el valor resultante en el perfil de Orca. |
| `guidance` | str | Qué hacer y qué observar. |
| `input` | objeto | Qué valor introduce el usuario (ver abajo). |
| `compute` | str | Función de `app/calc.py`: `identity`, `flow`, `pa_tower`, `mvs`. |
| `output` | str | Clave de resultado donde se guarda. Debe estar en `ALLOWED_OUTPUTS`. |
| `params` | objeto | Parámetros del test/cómputo (rangos de la torre, `base`, `step`…). |
| `warnings` | lista[str] | Avisos del material para este paso. |

### `input.kind`

| kind | Significado | Cómputo típico |
|------|-------------|----------------|
| `choice_value` | Valor leído directamente (p.ej. temperatura del mejor bloque). | `identity` |
| `value` | Valor numérico directo (p.ej. distancia de retracción). | `identity` |
| `modifier` | Delta del bloque elegido en el test de flow YOLO (se suma al flow actual). | `flow_yolo` |
| `height_mm` | Altura en mm leída en una torre (PA, MVS). | `pa_tower` / `mvs` |

## Cómputos (`app/calc.py`)

- `identity` → devuelve el valor introducido tal cual.
- `flow_yolo` → `flow_actual + delta` (método YOLO de OrcaSlicer, una pasada). El flow actual lo aporta el campo `ask_current`; si falta, usa `params.base` o 1.0.
- `pa_tower` → `params.start + params.step * altura_mm` (step 0.002/mm en direct drive, P1S). La torre PA no admite "imprimir números" (es un gradiente continuo): se mide la altura.
- `mvs` → `params.start + altura_mm * params.step`. La UI muestra además el valor con margen de seguridad (−15%).

## Outputs permitidos (`ALLOWED_OUTPUTS`)

`nozzle_temp`, `bed_temp`, `flow_ratio`, `pressure_advance`, `mvs`,
`retraction_distance`, `retraction_speed`.
