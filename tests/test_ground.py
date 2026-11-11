"""The ground and physics scene shared by every Primvaria project (granulaire/ground.py)."""

import pytest
from pxr import Usd

from granulaire.generator import generate_scene, write_outputs
from granulaire.ground import conformance, read_ground


def test_ground_and_physics_scene_follow_the_shared_convention(tmp_path):
    scene = generate_scene("glass_beads", shapes=4, copies=1)
    folder = write_outputs(scene, tmp_path)
    files = sorted(f for f in folder.rglob("*.usd*") if f.suffix in (".usd", ".usda", ".usdc"))
    assert files
    for f in files:
        stage = Usd.Stage.Open(str(f))
        if not stage.GetPrimAtPath("/World/PhysicsScene"):
            continue  # a layer without physics
        assert conformance(stage) == [], f
        g = read_ground(stage)
        assert g["top"] == pytest.approx(0.0, abs=1e-9)
        assert g["dynamic_friction"] == pytest.approx(0.5)
