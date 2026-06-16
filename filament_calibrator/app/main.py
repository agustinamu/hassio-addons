"""App web del calibrador (FastAPI + Jinja2 + HTMX).

UX con mejora progresiva: todo funciona con formularios y redirects normales;
HTMX (hx-boost) solo suaviza la navegación. Persistencia v1 = JSON local.
"""

from __future__ import annotations

import os
import re
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import calc
from .content import load_materials
from .models import FilamentRecord, Material
from .spoolman import SpoolmanClient
from .storage import LocalJsonStorage, StorageBackend

BASE_DIR = Path(__file__).resolve().parent

# Contenido estático (un YAML inválido aborta el arranque: a propósito) y storage
# por defecto. El storage se expone vía dependencia para poder sustituirlo en tests.
MATERIALS: dict[str, Material] = load_materials()

# Data dir configurable: el addon de HA monta /data persistente y pasa
# CALIBRATOR_DATA_DIR=/data. Sin la env, dev local usa el path por defecto.
def _resolve_storage() -> StorageBackend:
    data_dir = os.environ.get("CALIBRATOR_DATA_DIR")
    return LocalJsonStorage(Path(data_dir) / "filaments") if data_dir else LocalJsonStorage()


_storage: StorageBackend = _resolve_storage()

# Spoolman es opcional: solo si CALIBRATOR_SPOOLMAN_URL está definida.
_spoolman_url = os.environ.get("CALIBRATOR_SPOOLMAN_URL")
_spoolman: SpoolmanClient | None = SpoolmanClient(_spoolman_url) if _spoolman_url else None


def get_storage() -> StorageBackend:
    return _storage


def get_spoolman() -> SpoolmanClient | None:
    return _spoolman


StorageDep = Annotated[StorageBackend, Depends(get_storage)]
SpoolmanDep = Annotated["SpoolmanClient | None", Depends(get_spoolman)]

app = FastAPI(title="Filament Calibrator")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.middleware("http")
async def ingress_root_path(request: Request, call_next):
    """Bajo el ingress de HA el addon se sirve tras un prefijo con token, que HA
    envía en la cabecera X-Ingress-Path. Lo exponemos como root_path para que las
    plantillas y los redirects lo antepongan. Sin la cabecera (dev local / Docker
    directo) queda "" y todo resuelve en la raíz, igual que antes."""
    prefix = request.headers.get("X-Ingress-Path")
    if prefix:
        request.scope["root_path"] = prefix
    return await call_next(request)


def _fmt(value: float | None, ndigits: int = 0, dash: str = "—") -> str:
    """Formatea un número para la plantilla; `dash` si es None."""
    if value is None:
        return dash
    return str(round(value)) if ndigits == 0 else f"{value:.{ndigits}f}"


templates.env.filters["fmt"] = _fmt


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def _redirect(request: Request, url: str) -> RedirectResponse:
    # 303: tras un POST, el navegador hace GET de la ficha. Antepone el prefijo de
    # ingress (root_path) para que el Location sea válido tras el proxy de HA.
    prefix = request.scope.get("root_path", "")
    return RedirectResponse(f"{prefix}{url}", status_code=303)


def _load_or_404(storage: StorageBackend, slug: str) -> FilamentRecord:
    record = storage.get(slug)
    if record is None:
        raise HTTPException(status_code=404, detail="Filamento no encontrado")
    return record


@app.get("/")
def index(request: Request, storage: StorageDep):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"records": storage.list_records(), "materials": MATERIALS},
    )


@app.post("/filaments")
def create_filament(
    request: Request,
    storage: StorageDep,
    vendor: Annotated[str, Form()],
    name: Annotated[str, Form()],
    material: Annotated[str, Form()],
    color_hex: Annotated[str, Form()] = "",
):
    mat = MATERIALS.get(material)
    if mat is None:
        raise HTTPException(status_code=422, detail=f"Material desconocido: {material}")

    slug = slugify(f"{vendor}-{name}") or slugify(material)
    if storage.get(slug) is not None:
        return _redirect(request, f"/filaments/{slug}")

    record = FilamentRecord(
        slug=slug,
        vendor=vendor.strip(),
        name=name.strip(),
        material=material,
        color_hex=(color_hex.strip().lstrip("#") or None),
        density=mat.defaults.density,
        diameter=mat.defaults.diameter,
        load_temp=float(mat.defaults.nozzle_range[1]),  # punto de partida editable
    )
    # Valores fijados por material (no se calibran con un test).
    record.results.bed_temp = mat.defaults.bed_temp
    record.results.retraction_speed = mat.defaults.retraction_speed
    storage.save(record)
    return _redirect(request, f"/filaments/{slug}")


def _filament_context(record: FilamentRecord) -> dict:
    mat = MATERIALS[record.material]
    results = record.results.model_dump()
    steps = [
        {
            "step": step,
            "done": record.steps_progress.get(step.id, False),
            "value": results.get(step.output) if record.steps_progress.get(step.id) else None,
        }
        for step in mat.steps
    ]
    next_id = next(
        (s["step"].id for s in steps if not s["done"] and not s["step"].optional),
        None,
    )
    mvs = results.get("mvs")
    return {
        "record": record,
        "material": mat,
        "results": results,
        "steps": steps,
        "next_id": next_id,
        "mvs_safe": calc.mvs_safe(mvs) if mvs is not None else None,
    }


@app.get("/filaments/{slug}")
def filament_detail(request: Request, slug: str, storage: StorageDep, spoolman: SpoolmanDep):
    record = _load_or_404(storage, slug)
    context = _filament_context(record)
    context["spoolman_enabled"] = spoolman is not None
    return templates.TemplateResponse(request, "filament.html", context)


@app.post("/filaments/{slug}/steps/{step_id}")
def submit_step(
    request: Request,
    slug: str,
    step_id: str,
    storage: StorageDep,
    value: Annotated[float, Form()],
    current: Annotated[str, Form()] = "",
):
    record = _load_or_404(storage, slug)
    step = next((s for s in MATERIALS[record.material].steps if s.id == step_id), None)
    if step is None:
        raise HTTPException(status_code=404, detail="Paso no encontrado")

    results = record.results.model_dump()
    # Pasos con ask_current (p.ej. flow YOLO) reciben el valor de partida del perfil.
    if step.ask_current and current.strip():
        results[step.output] = float(current)
    computed = calc.compute(step.compute, value, step.params, results)
    setattr(record.results, step.output, computed)
    record.steps_progress[step.id] = True
    storage.save(record)
    return _redirect(request, f"/filaments/{slug}")


@app.post("/filaments/{slug}/meta")
def update_meta(
    request: Request,
    slug: str,
    storage: StorageDep,
    vendor: Annotated[str, Form()] = "",
    name: Annotated[str, Form()] = "",
    bed_temp: Annotated[str, Form()] = "",
    retraction_speed: Annotated[str, Form()] = "",
    load_temp: Annotated[str, Form()] = "",
    orca_profile: Annotated[str, Form()] = "",
    color_hex: Annotated[str, Form()] = "",
):
    record = _load_or_404(storage, slug)

    def _num(v: str) -> float | None:
        return float(v) if v.strip() else None

    # Renombrar (no cambia el slug: es la clave del fichero y el emparejamiento
    # con Spoolman vía calibrator_slug).
    if vendor.strip():
        record.vendor = vendor.strip()
    if name.strip():
        record.name = name.strip()
    if bed_temp.strip():
        record.results.bed_temp = _num(bed_temp)
    if retraction_speed.strip():
        record.results.retraction_speed = _num(retraction_speed)
    if load_temp.strip():
        record.load_temp = _num(load_temp)
    record.orca_profile = orca_profile.strip() or None
    record.color_hex = color_hex.strip().lstrip("#") or None
    storage.save(record)
    return _redirect(request, f"/filaments/{slug}")


@app.post("/filaments/{slug}/finalize")
def finalize(request: Request, slug: str, storage: StorageDep):
    record = _load_or_404(storage, slug)
    record.calibrated = True
    record.calib_date = date.today().isoformat()
    storage.save(record)
    return _redirect(request, f"/filaments/{slug}")


@app.post("/filaments/{slug}/sync")
def sync_to_spoolman(request: Request, slug: str, storage: StorageDep, spoolman: SpoolmanDep):
    record = _load_or_404(storage, slug)
    if spoolman is None:
        raise HTTPException(
            status_code=400, detail="Spoolman no configurado (CALIBRATOR_SPOOLMAN_URL)"
        )
    try:
        spoolman.sync_filament(record, MATERIALS[record.material].name)
    except Exception as exc:  # red/HTTP de Spoolman: error claro, no 500 opaco
        raise HTTPException(
            status_code=502, detail=f"Error sincronizando con Spoolman: {exc}"
        ) from exc
    return _redirect(request, f"/filaments/{slug}")


@app.post("/filaments/{slug}/delete")
def delete_filament(request: Request, slug: str, storage: StorageDep):
    storage.delete(slug)
    return _redirect(request, "/")
