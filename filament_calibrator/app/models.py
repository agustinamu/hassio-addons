"""Modelos de dominio: contenido de calibración (YAML) y registro de filamento.

El contenido de calibración es *data-driven*: cada material declara, en su YAML,
una lista ordenada de pasos. La app no conoce los materiales; solo el esquema.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

# Claves de resultado que un paso puede producir (campo `output` del paso) y que
# además son los campos persistidos en CalibResults. Cualquier `output` fuera de
# este conjunto es un error de contenido.
ALLOWED_OUTPUTS = {
    "nozzle_temp",
    "bed_temp",
    "flow_ratio",
    "pressure_advance",
    "mvs",
    "retraction_distance",
    "retraction_speed",
}

# Funciones de cálculo disponibles (registry en calc.py). Validar aquí evita
# YAML que apunte a un cómputo inexistente.
ALLOWED_COMPUTERS = {"identity", "flow_yolo", "pa_tower", "mvs"}

# Tipo de dato que el paso pide al usuario.
InputKind = Literal["choice_value", "height_mm", "modifier", "value"]


class StepInput(BaseModel):
    """Qué valor introduce el usuario tras observar el test impreso."""

    kind: InputKind
    label: str
    unit: str | None = None


class Step(BaseModel):
    """Un paso de calibración dentro de un material."""

    id: str
    title: str
    optional: bool = False
    # Si True, el paso pide además el valor actual del perfil (base del cálculo),
    # p.ej. el flow ratio de partida en los pasos de flow.
    ask_current: bool = False
    orca_path: str  # dónde lanzar el test en Orca
    orca_apply: str  # dónde meter el valor resultante en el perfil de Orca
    guidance: str
    input: StepInput
    compute: str
    output: str
    params: dict = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("compute")
    @classmethod
    def _known_compute(cls, v: str) -> str:
        if v not in ALLOWED_COMPUTERS:
            raise ValueError(f"compute desconocido: {v!r} (válidos: {sorted(ALLOWED_COMPUTERS)})")
        return v

    @field_validator("output")
    @classmethod
    def _known_output(cls, v: str) -> str:
        if v not in ALLOWED_OUTPUTS:
            raise ValueError(f"output desconocido: {v!r} (válidos: {sorted(ALLOWED_OUTPUTS)})")
        return v


class MaterialDefaults(BaseModel):
    density: float
    diameter: float = 1.75
    nozzle_range: tuple[int, int]
    bed_range: tuple[int, int]
    # Perfil de Orca del que partir antes de calibrar (se duplica y se renombra).
    base_profile: str
    # Valores fijados por material (no se calibran con un test en v1):
    bed_temp: int
    retraction_speed: int


class Material(BaseModel):
    """Definición completa de un material y su proceso de calibración."""

    code: str
    name: str
    defaults: MaterialDefaults
    steps: list[Step]

    @field_validator("steps")
    @classmethod
    def _unique_step_ids(cls, steps: list[Step]) -> list[Step]:
        ids = [s.id for s in steps]
        if len(ids) != len(set(ids)):
            raise ValueError(f"ids de paso duplicados en material: {ids}")
        return steps


class CalibResults(BaseModel):
    """Valores calibrados de un filamento. Todos opcionales: se rellenan a medida."""

    nozzle_temp: float | None = None
    bed_temp: float | None = None
    flow_ratio: float | None = None
    pressure_advance: float | None = None
    mvs: float | None = None
    retraction_distance: float | None = None
    retraction_speed: float | None = None


class FilamentRecord(BaseModel):
    """Lo que la app persiste por filamento (JSON local en v1; Spoolman después)."""

    slug: str
    vendor: str
    name: str
    material: str  # código de material (pla, petg, tpu90a)
    color_hex: str | None = None
    density: float
    diameter: float = 1.75
    results: CalibResults = Field(default_factory=CalibResults)
    orca_profile: str | None = None
    load_temp: float | None = None
    calibrated: bool = False
    calib_date: str | None = None
    # step_id -> completado. Permite reanudar y repetir pasos sueltos.
    steps_progress: dict[str, bool] = Field(default_factory=dict)
