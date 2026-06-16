"""Tests de carga y validación del contenido YAML de materiales."""

import pytest

from app.content import load_materials
from app.models import ALLOWED_COMPUTERS, ALLOWED_OUTPUTS


@pytest.fixture(scope="module")
def materials():
    return load_materials()


def test_loads_three_materials(materials):
    assert set(materials.keys()) == {"pla", "petg", "tpu90a"}


def test_all_steps_use_known_compute_and_output(materials):
    for material in materials.values():
        for step in material.steps:
            assert step.compute in ALLOWED_COMPUTERS
            assert step.output in ALLOWED_OUTPUTS


def test_step_ids_unique_per_material(materials):
    for material in materials.values():
        ids = [s.id for s in material.steps]
        assert len(ids) == len(set(ids))


def test_tpu_marks_pa_and_mvs_optional(materials):
    tpu = materials["tpu90a"]
    optional = {s.id for s in tpu.steps if s.optional}
    assert {"pressure_advance", "mvs"} <= optional


def test_defaults_present(materials):
    for material in materials.values():
        d = material.defaults
        assert d.density > 0
        assert d.nozzle_range[0] < d.nozzle_range[1]
        assert d.bed_temp >= 0
