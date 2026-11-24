"""What Newton needs and cannot guess is a layer over the file, not part of the file."""

import pytest
from pxr import Sdf, Usd, UsdPhysics

from granulaire import contract, newton
from granulaire.cli import main
from granulaire.generator import generate_scene, write_outputs
from granulaire.validate import validate


@pytest.mark.parametrize("key", ["crushed_gravel", "beach_sand", "packing_peanuts"])
def test_the_file_has_its_newton_layer(key, tmp_path):
    folder = write_outputs(generate_scene(key, shapes=3, copies=2, seed=1), tmp_path)
    layer = folder / f"granulaire_{key}_newton.usda"
    assert newton.overlay_path(folder / f"granulaire_{key}.usdc") == layer and layer.exists()
    assert list(Sdf.Layer.FindOrOpen(str(layer)).subLayerPaths) == [f"./granulaire_{key}.usdc"]
    assert newton.check(layer) == []
    assert validate(layer) == []
    assert contract.check(layer) == []
    assert contract.engine_data(Usd.Stage.Open(str(folder / f"granulaire_{key}.usdc"))) == []
    assert newton.main([str(folder)]) == 0


def test_every_grain_gets_a_quarter_of_its_smallest_extent(tmp_path):
    folder = write_outputs(generate_scene("beach_sand", shapes=3, copies=2, seed=1), tmp_path)
    stage = Usd.Stage.Open(str(folder / "granulaire_beach_sand_newton.usda"))
    grains = [
        p for p in stage.Traverse() if p.HasAPI(UsdPhysics.CollisionAPI) and "/Grains/" in str(p.GetPath())
    ]
    assert len(grains) == 6
    for g in grains:  # read through the reference to the prototype
        gap = g.GetAttribute(newton.GAP).Get()
        assert gap == pytest.approx(newton.contact_gap(g), rel=1e-6)
        assert 1e-6 < gap < 2e-4  # sand: far below the 0.5 mm cap, and far below Newton's 0.1 m


def test_a_collider_without_a_gap_is_refused(tmp_path):
    folder = write_outputs(generate_scene("crushed_gravel", shapes=2, copies=1, seed=1), tmp_path)
    layer = folder / "granulaire_crushed_gravel_newton.usda"
    stage = Usd.Stage.Open(str(layer))
    proto = next(p for p in Usd.PrimRange.AllPrims(stage.GetPseudoRoot()) if p.HasAttribute(newton.GAP))
    proto.RemoveProperty(newton.GAP)
    stage.GetRootLayer().Save()
    assert any("without" in p for p in newton.check(layer))


@pytest.mark.parametrize(
    ("engines", "newton_", "omni"), [("none", 0, 0), ("newton", 1, 0), ("omniphysics", 0, 1)]
)
def test_engines_chooses_the_layers(tmp_path, engines, newton_, omni):
    args = ["generate", "--preset", "packing_peanuts", "--shapes", "2", "--copies", "1"]
    assert main([*args, "--out", str(tmp_path), "--engines", engines]) == 0
    assert len(list(tmp_path.rglob("*_newton.usda"))) == newton_
    assert len(list(tmp_path.rglob("*_omniphysics.usd*"))) == omni
