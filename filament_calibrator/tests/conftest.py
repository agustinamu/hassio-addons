import pytest
from starlette.testclient import TestClient

from app.main import app, get_storage
from app.storage import LocalJsonStorage


@pytest.fixture
def storage(tmp_path):
    """Storage aislado por test: no toca data/ real."""
    return LocalJsonStorage(tmp_path / "filaments")


@pytest.fixture
def client(storage):
    app.dependency_overrides[get_storage] = lambda: storage
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
