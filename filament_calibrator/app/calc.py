"""Fórmulas de calibración.

Cada cómputo recibe:
  - value: el número que introdujo el usuario tras leer el test.
  - params: los parámetros del paso (del YAML del material).
  - results: los resultados ya calibrados del filamento (para dependencias entre
    pasos, p.ej. flow Pass 2 parte del flow ratio de Pass 1).

Devuelve el valor final a guardar en el `output` del paso.

Referencias (verificadas, ver plan):
  - flow ratio (YOLO):  new = old + delta   (método de una pasada de OrcaSlicer)
  - factor K (PA tower): pa = start + step * altura_mm  (step 0.002/mm direct drive, P1S)
  - MVS:                mvs = start + altura_mm * step
"""

from __future__ import annotations

from collections.abc import Callable

# Margen de seguridad recomendado para MVS (restar ~15% al resultado del test).
MVS_SAFETY_FACTOR = 0.85


def _identity(value: float, params: dict, results: dict) -> float:
    return value


def _flow_yolo(value: float, params: dict, results: dict) -> float:
    # Método YOLO de OrcaSlicer (una pasada): `value` es el delta del mejor
    # bloque y se SUMA al flow de partida (el actual del perfil de Orca).
    old = results.get("flow_ratio")
    if old is None:
        old = params.get("base", 1.0)
    return round(old + value, 4)


def _pa_tower(value: float, params: dict, results: dict) -> float:
    # `value` es la altura (mm) de la mejor zona; el PA sube `step` por mm.
    start = params.get("start", 0.0)
    step = params.get("step", 0.002)
    return round(start + step * value, 4)


def _mvs(value: float, params: dict, results: dict) -> float:
    # `value` es la altura (mm) donde empieza a degradarse la calidad.
    start = params.get("start", 5.0)
    step = params.get("step", 0.5)
    return start + value * step


COMPUTERS: dict[str, Callable[[float, dict, dict], float]] = {
    "identity": _identity,
    "flow_yolo": _flow_yolo,
    "pa_tower": _pa_tower,
    "mvs": _mvs,
}


def compute(name: str, value: float, params: dict, results: dict) -> float:
    """Aplica el cómputo `name`. Lanza KeyError si no existe (validado en modelos)."""
    return COMPUTERS[name](value, params, results)


def mvs_safe(mvs_value: float) -> float:
    """MVS con margen de seguridad recomendado."""
    return round(mvs_value * MVS_SAFETY_FACTOR, 2)
