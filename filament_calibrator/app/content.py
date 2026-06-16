"""Carga y validación del contenido de calibración (YAML por material).

El contenido vive en `content/materials/*.yaml` y *es* la documentación del
proceso. Aquí solo se carga y valida contra los modelos Pydantic.
"""

from __future__ import annotations

from pathlib import Path

import yaml

from .models import Material

# content/materials relativo a la raíz del proyecto (calibrator/).
DEFAULT_CONTENT_DIR = Path(__file__).resolve().parent.parent / "content" / "materials"


def load_materials(content_dir: Path | None = None) -> dict[str, Material]:
    """Carga todos los YAML de materiales. La clave del dict es el `code`.

    Lanza ValueError si un archivo no valida o si hay códigos duplicados.
    """
    directory = content_dir or DEFAULT_CONTENT_DIR
    materials: dict[str, Material] = {}
    for path in sorted(directory.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        try:
            material = Material.model_validate(raw)
        except Exception as exc:  # noqa: BLE001 - re-empaquetar con el archivo culpable
            raise ValueError(f"contenido inválido en {path.name}: {exc}") from exc
        if material.code in materials:
            raise ValueError(f"código de material duplicado: {material.code!r} ({path.name})")
        materials[material.code] = material
    return materials


def get_material(code: str, content_dir: Path | None = None) -> Material | None:
    return load_materials(content_dir).get(code)
