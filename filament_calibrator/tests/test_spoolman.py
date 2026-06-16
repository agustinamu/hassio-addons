"""Tests del adaptador Spoolman con una API simulada (httpx.MockTransport)."""

import json

import httpx

from app.main import app, get_spoolman
from app.models import CalibResults, FilamentRecord
from app.spoolman import SpoolmanClient


class FakeSpoolman:
    """API de Spoolman en memoria para los tests."""

    def __init__(self):
        self.vendors: list[dict] = []
        self.fields: list[dict] = []
        self.filaments: list[dict] = []
        self.calls: list[tuple[str, str]] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        path, method = request.url.path, request.method
        self.calls.append((method, path))
        body = json.loads(request.content) if request.content else {}

        if path == "/api/v1/vendor" and method == "GET":
            return httpx.Response(200, json=self.vendors)
        if path == "/api/v1/vendor" and method == "POST":
            v = {"id": len(self.vendors) + 1, **body}
            self.vendors.append(v)
            return httpx.Response(200, json=v)
        if path == "/api/v1/field/filament" and method == "GET":
            return httpx.Response(200, json=self.fields)
        if path.startswith("/api/v1/field/filament/") and method == "POST":
            self.fields.append({"key": path.rsplit("/", 1)[1], **body})
            return httpx.Response(200, json=self.fields[-1])
        if path == "/api/v1/filament" and method == "GET":
            return httpx.Response(200, json=self.filaments)
        if path == "/api/v1/filament" and method == "POST":
            fil = {"id": len(self.filaments) + 1, **body}
            self.filaments.append(fil)
            return httpx.Response(200, json=fil)
        if path.startswith("/api/v1/filament/") and method == "PATCH":
            fid = int(path.rsplit("/", 1)[1])
            fil = next(f for f in self.filaments if f["id"] == fid)
            fil.update(body)
            return httpx.Response(200, json=fil)
        return httpx.Response(404, json={})


def _client(fake: FakeSpoolman) -> SpoolmanClient:
    transport = httpx.MockTransport(fake.handler)
    return SpoolmanClient("http://test", client=httpx.Client(transport=transport))


def _record(**over) -> FilamentRecord:
    data = dict(
        slug="acme-negro",
        vendor="Acme",
        name="Negro",
        material="petg",
        density=1.27,
        results=CalibResults(nozzle_temp=245, bed_temp=75, flow_ratio=1.02, pressure_advance=0.025),
    )
    data.update(over)
    return FilamentRecord(**data)


def test_sync_creates_filament_with_json_encoded_extra():
    fake = FakeSpoolman()
    fid = _client(fake).sync_filament(_record(), "PETG")

    assert fid == 1
    fil = fake.filaments[0]
    assert fil["material"] == "PETG"
    assert fil["vendor_id"] == 1
    assert fil["settings_extruder_temp"] == 245
    # los valores de extra van como strings JSON
    assert fil["extra"]["factor_k"] == "0.025"
    assert json.loads(fil["extra"]["calibrator_slug"]) == "acme-negro"
    assert json.loads(fil["extra"]["flow_ratio"]) == 1.02


def test_sync_is_idempotent_updates_existing():
    fake = FakeSpoolman()
    client = _client(fake)
    client.sync_filament(_record(), "PETG")
    client.sync_filament(_record(results=CalibResults(pressure_advance=0.030)), "PETG")

    assert len(fake.filaments) == 1  # no duplica
    assert ("PATCH", "/api/v1/filament/1") in fake.calls
    assert fake.filaments[0]["extra"]["factor_k"] == "0.03"


def test_read_merge_write_preserves_foreign_extra():
    fake = FakeSpoolman()
    # filamento preexistente con un extra de otra integración
    fake.filaments.append(
        {
            "id": 1,
            "extra": {"calibrator_slug": '"acme-negro"', "foreign": '"keep-me"'},
        }
    )
    fake.vendors.append({"id": 1, "name": "Acme"})
    _client(fake).sync_filament(_record(), "PETG")

    extra = fake.filaments[0]["extra"]
    assert extra["foreign"] == '"keep-me"'  # no se pisa
    assert extra["factor_k"] == "0.025"  # se añade el nuestro


def test_vendor_is_reused_not_duplicated():
    fake = FakeSpoolman()
    client = _client(fake)
    client.sync_filament(_record(), "PETG")
    client.sync_filament(_record(slug="acme-rojo", name="Rojo"), "PETG")
    assert len(fake.vendors) == 1


def test_sync_endpoint_wires_through(client, storage):
    fake = FakeSpoolman()
    app.dependency_overrides[get_spoolman] = lambda: _client(fake)
    client.post("/filaments", data={"vendor": "Acme", "name": "Negro", "material": "petg"})
    r = client.post("/filaments/acme-negro/sync", follow_redirects=False)
    assert r.status_code == 303
    assert len(fake.filaments) == 1
