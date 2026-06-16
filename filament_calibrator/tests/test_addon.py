"""Tests del empaquetado addon: data dir configurable y soporte de ingress de HA.

El addon corre detrás del ingress de HA, que sirve la app bajo un prefijo con token
(cabecera X-Ingress-Path). Las URLs generadas y los redirects deben llevar ese
prefijo; sin la cabecera, todo debe quedar igual que en dev local.
"""

from pathlib import Path

from app.main import _resolve_storage

INGRESS = "/api/hassio_ingress/abc123"


def _create_petg(client):
    return client.post(
        "/filaments",
        data={"vendor": "Test", "name": "Smoke", "material": "petg"},
        follow_redirects=False,
    )


# --- CALIBRATOR_DATA_DIR ---


def test_data_dir_env_is_honored(monkeypatch, tmp_path):
    monkeypatch.setenv("CALIBRATOR_DATA_DIR", str(tmp_path))
    storage = _resolve_storage()
    assert storage.data_dir == tmp_path / "filaments"


def test_data_dir_default_without_env(monkeypatch):
    monkeypatch.delenv("CALIBRATOR_DATA_DIR", raising=False)
    storage = _resolve_storage()
    # Sin env, el path por defecto del repo (no /data).
    assert storage.data_dir.name == "filaments"
    assert "data" in str(storage.data_dir)


# --- ingress: sin cabecera, comportamiento idéntico a hoy ---


def test_no_ingress_uses_root_paths(client):
    _create_petg(client)
    r = client.get("/filaments/test-smoke")
    assert 'action="/filaments/test-smoke/meta"' in r.text
    assert 'href="/static/style.css"' in r.text


def test_no_ingress_redirect_location_is_plain(client):
    r = _create_petg(client)
    assert r.headers["location"] == "/filaments/test-smoke"


# --- ingress: con cabecera, las URLs y el Location llevan el prefijo ---


def test_ingress_prefixes_links(client):
    _create_petg(client)
    r = client.get("/filaments/test-smoke", headers={"X-Ingress-Path": INGRESS})
    assert f'action="{INGRESS}/filaments/test-smoke/meta"' in r.text
    assert f'href="{INGRESS}/static/style.css"' in r.text


def test_ingress_prefixes_redirect_location(client):
    r = client.post(
        "/filaments/test-smoke/finalize",  # no existe -> 404, no redirige
        headers={"X-Ingress-Path": INGRESS},
        follow_redirects=False,
    )
    assert r.status_code == 404  # guard: finalize sobre inexistente

    _create_petg(client)
    r = client.post(
        "/filaments/test-smoke/finalize",
        headers={"X-Ingress-Path": INGRESS},
        follow_redirects=False,
    )
    assert r.headers["location"] == f"{INGRESS}/filaments/test-smoke"


# --- renombrado vía /meta (no cambia el slug) ---


def test_meta_renames_without_changing_slug(client, storage):
    _create_petg(client)
    client.post(
        "/filaments/test-smoke/meta",
        data={"vendor": "SUNLU", "name": "Blanco Brillante"},
        follow_redirects=False,
    )
    rec = storage.get("test-smoke")  # slug intacto
    assert rec is not None
    assert rec.vendor == "SUNLU"
    assert rec.name == "Blanco Brillante"


def test_meta_blank_name_keeps_previous(client, storage):
    _create_petg(client)
    client.post("/filaments/test-smoke/meta", data={"name": ""}, follow_redirects=False)
    assert storage.get("test-smoke").name == "Smoke"


def test_resolve_storage_returns_path(monkeypatch, tmp_path):
    monkeypatch.setenv("CALIBRATOR_DATA_DIR", str(tmp_path))
    assert isinstance(_resolve_storage().data_dir, Path)
