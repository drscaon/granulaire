"""Physics checks read back from the files: the pile tests in MuJoCo and Blender."""

import importlib.util

import pytest

from granulaire import Variations, generate_scene, write_outputs


@pytest.fixture(scope="module")
def gravel(tmp_path_factory):
    scene = generate_scene("crushed_gravel", shapes=6, copies=2, variations=Variations(moisture=True))
    return write_outputs(scene, tmp_path_factory.mktemp("pile"))


def test_reader_reads_the_physics(gravel):
    from granulaire.sim.scene import read_scene

    scene = read_scene(gravel)
    assert len(scene.grains) == 12
    assert all(g.mass > 0 and 0 < g.friction < 2 and g.thickness <= g.size * 2 for g in scene.grains)
    assert scene.deformable == 0


@pytest.mark.skipif(importlib.util.find_spec("mujoco") is None, reason="MuJoCo not installed")
def test_mujoco_pile(gravel):
    from granulaire.sim import mujoco_test

    report = mujoco_test.run(gravel)
    assert report["passed"], report["checks"]
    assert report["length_factor"] > 1  # 6 mm grains run scaled up
    assert (gravel / "sim_test" / "mujoco_pile.xml").exists()


@pytest.mark.skipif(importlib.util.find_spec("mujoco") is None, reason="MuJoCo not installed")
def test_mujoco_sand_at_scale(tmp_path):
    """Sand grains (0.35 mm) settle when run in scaled units."""
    from granulaire.sim import mujoco_test

    folder = write_outputs(generate_scene("beach_sand", shapes=8, copies=1), tmp_path)
    report = mujoco_test.run(folder)
    assert report["passed"], report["checks"]


def test_deformable_grains_are_not_rigid(tmp_path):
    from granulaire.sim.scene import read_scene

    folder = write_outputs(generate_scene("packing_peanuts", shapes=2, copies=1), tmp_path)
    assert read_scene(folder).deformable == 2


@pytest.mark.skipif(importlib.util.find_spec("bpy") is None, reason="Blender (bpy) not installed")
def test_blender_pile(gravel):
    from granulaire.blender import pile_test

    report = pile_test.run(gravel)
    assert report["passed"], report["checks"]
