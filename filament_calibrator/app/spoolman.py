"""Adaptador a Spoolman: exporta un filamento calibrado al inventario.

Modelo de uso (fase 3): el storage local sigue siendo la fuente de verdad del
*proceso* de calibración; cuando un filamento está listo, se *sincroniza* a
Spoolman a nivel de **Filament** (no Spool — las bobinas/gramos los gestiona
SpoolmanSync). Idempotente: se empareja por el custom field `calibrator_slug`.

Particularidades verificadas de la API de Spoolman (ver plan):
  - La API no tiene autenticación; base en `http://host:7912/api/v1`.
  - Los valores del campo `extra` deben ser **strings JSON** (un número va como
    "0.025", un texto como "\\"PETG\\""). Por eso codificamos con json.dumps.
  - Un PATCH de `extra` **reemplaza** todo el objeto extra → hacemos
    read-merge-write para no pisar campos de otras integraciones.
  - Los custom fields deben **definirse** antes de poder escribirlos.

Esta lógica está construida sobre la documentación de la API; debe validarse
contra una instancia real al montar el addon.
"""

from __future__ import annotations

import json

import httpx

from .models import FilamentRecord

# Custom fields que definimos en Spoolman para el entity_type `filament`.
# (clave, tipo) — tipos soportados: text, float, integer.
CUSTOM_FIELDS: list[tuple[str, str]] = [
    ("calibrator_slug", "text"),  # clave de emparejamiento idempotente
    ("factor_k", "float"),
    ("flow_ratio", "float"),
    ("mvs", "float"),
    ("retraction_distance", "float"),
    ("retraction_speed", "float"),
    ("load_temp", "float"),
    ("orca_profile", "text"),
    ("calib_date", "text"),
]


def _enc(value: object) -> str:
    """Codifica un valor para el campo `extra` (Spoolman exige strings JSON)."""
    return json.dumps(value)


def _dec(value: object) -> object:
    """Decodifica un valor del campo `extra`. Tolerante a valores ya planos."""
    if not isinstance(value, str):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _build_extra(record: FilamentRecord) -> dict[str, str]:
    r = record.results
    raw = {
        "calibrator_slug": record.slug,
        "factor_k": r.pressure_advance,
        "flow_ratio": r.flow_ratio,
        "mvs": r.mvs,
        "retraction_distance": r.retraction_distance,
        "retraction_speed": r.retraction_speed,
        "load_temp": record.load_temp,
        "orca_profile": record.orca_profile,
        "calib_date": record.calib_date,
    }
    return {k: _enc(v) for k, v in raw.items() if v is not None}


def _standard_fields(record: FilamentRecord, vendor_id: int, material_name: str) -> dict:
    fields: dict = {
        "name": record.name,
        "vendor_id": vendor_id,
        "material": material_name,
        "density": record.density,
        "diameter": record.diameter,
    }
    if record.color_hex:
        fields["color_hex"] = record.color_hex
    if record.results.nozzle_temp is not None:
        fields["settings_extruder_temp"] = int(record.results.nozzle_temp)
    if record.results.bed_temp is not None:
        fields["settings_bed_temp"] = int(record.results.bed_temp)
    return fields


class SpoolmanClient:
    """Cliente mínimo de la API de Spoolman para exportar filamentos."""

    def __init__(self, base_url: str, client: httpx.Client | None = None, timeout: float = 10.0):
        self.api = base_url.rstrip("/") + "/api/v1"
        self._client = client or httpx.Client(timeout=timeout)

    def close(self) -> None:
        self._client.close()

    # --- helpers HTTP ---
    def _get(self, path: str):
        r = self._client.get(self.api + path)
        r.raise_for_status()
        return r.json()

    def _post(self, path: str, payload: dict):
        r = self._client.post(self.api + path, json=payload)
        r.raise_for_status()
        return r.json()

    def _patch(self, path: str, payload: dict):
        r = self._client.patch(self.api + path, json=payload)
        r.raise_for_status()
        return r.json()

    # --- operaciones ---
    def ensure_vendor(self, name: str) -> int:
        for v in self._get("/vendor"):
            if v.get("name", "").strip().lower() == name.strip().lower():
                return v["id"]
        return self._post("/vendor", {"name": name})["id"]

    def ensure_custom_fields(self) -> None:
        try:
            existing = {f.get("key") or f.get("name") for f in self._get("/field/filament")}
        except httpx.HTTPStatusError:
            existing = set()
        for key, ftype in CUSTOM_FIELDS:
            if key in existing:
                continue
            try:
                self._post(f"/field/filament/{key}", {"name": key, "field_type": ftype})
            except httpx.HTTPStatusError:
                # Ya existe o definido por otra vía: no es fatal.
                pass

    def find_by_slug(self, slug: str) -> dict | None:
        for f in self._get("/filament"):
            extra = f.get("extra") or {}
            if _dec(extra.get("calibrator_slug")) == slug:
                return f
        return None

    def sync_filament(self, record: FilamentRecord, material_name: str) -> int:
        """Crea o actualiza el filamento en Spoolman. Devuelve su id."""
        vendor_id = self.ensure_vendor(record.vendor)
        self.ensure_custom_fields()

        existing = self.find_by_slug(record.slug)
        # read-merge-write del extra para no pisar campos de otras integraciones.
        extra = dict((existing or {}).get("extra") or {})
        extra.update(_build_extra(record))

        payload = _standard_fields(record, vendor_id, material_name)
        payload["extra"] = extra

        if existing:
            return self._patch(f"/filament/{existing['id']}", payload)["id"]
        return self._post("/filament", payload)["id"]
