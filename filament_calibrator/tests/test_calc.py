"""Tests de las fórmulas de calibración."""

import math

from app import calc


def test_identity():
    assert calc.compute("identity", 245, {}, {}) == 245


def test_flow_yolo_adds_delta_to_current():
    # YOLO: flow actual 0.95 + delta -0.01 -> 0.94
    out = calc.compute("flow_yolo", -0.01, {}, {"flow_ratio": 0.95})
    assert math.isclose(out, 0.94)


def test_flow_yolo_positive_delta():
    out = calc.compute("flow_yolo", 0.02, {}, {"flow_ratio": 0.98})
    assert math.isclose(out, 1.0)


def test_flow_yolo_falls_back_to_base_when_no_current():
    out = calc.compute("flow_yolo", -0.01, {"base": 1.0}, {})
    assert math.isclose(out, 0.99)


def test_pa_tower_direct_drive():
    # start 0, step 0.002/mm, altura 15 mm -> 0.03
    out = calc.compute("pa_tower", 15, {"start": 0.0, "step": 0.002}, {})
    assert math.isclose(out, 0.03)


def test_mvs():
    # start 5, step 0.5, altura 18 mm -> 5 + 9 = 14
    out = calc.compute("mvs", 18, {"start": 5, "step": 0.5}, {})
    assert math.isclose(out, 14.0)


def test_mvs_safe_margin():
    assert calc.mvs_safe(14.0) == 11.9  # 14 * 0.85
