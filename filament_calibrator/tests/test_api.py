"""Tests de la API web con storage aislado (ver conftest.py)."""


def _create_petg(client):
    return client.post(
        "/filaments",
        data={"vendor": "Test", "name": "Smoke", "material": "petg"},
        follow_redirects=False,
    )


def test_index_empty(client):
    assert client.get("/").status_code == 200


def test_detail_renders_with_empty_results(client):
    """La ficha recién creada (valores None) renderiza sin error (filtro fmt)."""
    _create_petg(client)
    r = client.get("/filaments/test-smoke")
    assert r.status_code == 200
    assert "—" in r.text  # campos sin calibrar muestran guion


def test_create_applies_material_defaults(client, storage):
    r = _create_petg(client)
    assert r.status_code == 303
    assert r.headers["location"] == "/filaments/test-smoke"
    rec = storage.get("test-smoke")
    assert rec.material == "petg"
    assert rec.results.bed_temp == 70  # default de petg.yaml
    assert rec.results.retraction_speed == 40


def test_unknown_material_is_422(client):
    r = client.post(
        "/filaments",
        data={"vendor": "X", "name": "Y", "material": "nope"},
        follow_redirects=False,
    )
    assert r.status_code == 422


def test_missing_filament_is_404(client):
    assert client.get("/filaments/no-existe").status_code == 404


def test_flow_yolo_adds_delta_to_current_flow(client, storage):
    _create_petg(client)
    # YOLO: el paso pide el flow actual del perfil (0.95) y el delta del bloque.
    # 0.95 + (-0.01) = 0.94
    client.post("/filaments/test-smoke/steps/flow", data={"current": "0.95", "value": -0.01})
    assert abs(storage.get("test-smoke").results.flow_ratio - 0.94) < 1e-9


def test_full_calibration_flow_computes_values(client, storage):
    _create_petg(client)
    client.post("/filaments/test-smoke/steps/temperature", data={"value": 245})
    client.post("/filaments/test-smoke/steps/flow", data={"current": "0.95", "value": -0.01})
    client.post("/filaments/test-smoke/steps/pressure_advance", data={"value": 15})
    client.post("/filaments/test-smoke/steps/mvs", data={"value": 10})

    res = storage.get("test-smoke").results
    assert res.nozzle_temp == 245
    assert abs(res.flow_ratio - 0.94) < 1e-9  # YOLO: 0.95 + (-0.01)
    assert abs(res.pressure_advance - 0.03) < 1e-9  # torre: 0.002/mm * 15mm
    assert abs(res.mvs - 10.0) < 1e-9

    client.post("/filaments/test-smoke/finalize")
    assert storage.get("test-smoke").calibrated is True
    assert client.get("/filaments/test-smoke").status_code == 200


def test_submit_step_on_missing_filament_is_404(client):
    r = client.post("/filaments/no-existe/steps/temperature", data={"value": 200})
    assert r.status_code == 404
