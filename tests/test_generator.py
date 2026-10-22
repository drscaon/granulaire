import json

import numpy as np
import pytest
from pxr import Usd, UsdPhysics, UsdShade

from granulat import Variations, generate_scene, write_outputs

SMALL = {"shapes": 6, "copies": 2, "seed": 7}


def _diameters(scene):
    return np.array([p["metrics"]["diameter_nominal_m"] for p in scene.prototypes])


def test_scene_counts():
    scene = generate_scene("crushed_gravel", **SMALL)
    assert len(scene.prototypes) == 6
    assert len(scene.instances) == 12
    assert sorted(np.bincount([i["proto"] for i in scene.instances])) == [2] * 6


def test_size_off_gives_a_single_diameter():
    scene = generate_scene("rounded_gravel", **SMALL, variations=Variations(size=False))
    d = _diameters(scene)
    assert d.max() == pytest.approx(d.min(), rel=1e-6)


def test_variations_do_not_shift_other_draws():
    ref = generate_scene("beach_sand", **SMALL)
    no_orient = generate_scene("beach_sand", **SMALL, variations=Variations(orientation=False))
    wet = generate_scene("beach_sand", **SMALL, variations=Variations(moisture=True))
    for other in (no_orient, wet):
        np.testing.assert_allclose(_diameters(other), _diameters(ref))
        assert [i["position"] for i in other.instances] == [i["position"] for i in ref.instances]
    assert all(i["orient"] == (1.0, 0.0, 0.0, 0.0) for i in no_orient.instances)


def test_moisture_is_ignored_for_regolith():
    scene = generate_scene("lunar_regolith", **SMALL, variations=Variations(moisture=True))
    assert scene.states is None
    assert scene.variations.moisture is False


def test_unknown_preset():
    with pytest.raises(KeyError):
        generate_scene("not_a_preset", **SMALL)


def test_usd_moisture_variants_are_consistent(tmp_path):
    scene = generate_scene("beach_pebbles", **SMALL, variations=Variations(moisture=True))
    folder = write_outputs(scene, tmp_path)
    stage = Usd.Stage.Open(str(folder / "granulat_beach_pebbles.usdc"))
    grains = stage.GetPrimAtPath("/World/Grains").GetChildren()
    assert len(grains) == 12
    for prim, inst in zip(grains, scene.instances, strict=True):
        state = prim.GetVariantSets().GetVariantSet("moisture").GetVariantSelection()
        assert state == inst["state"]
        expected = scene.prototypes[inst["proto"]]["moisture"][state]["mass"]
        assert UsdPhysics.MassAPI(prim).GetMassAttr().Get() == pytest.approx(expected, rel=1e-6)
        geom = prim.GetChild("geom")
        assert UsdShade.MaterialBindingAPI(geom).ComputeBoundMaterial()[0].GetPath().name.endswith(state)
        physics = UsdShade.MaterialBindingAPI(geom).ComputeBoundMaterial("physics")[0]
        assert physics.GetPath().name == f"Phys_{state}"

    # switching a grain's variant changes its mass without regenerating
    g = grains[0]
    g.GetVariantSets().GetVariantSet("moisture").SetVariantSelection("saturated")
    sat = scene.prototypes[scene.instances[0]["proto"]]["moisture"]["saturated"]["mass"]
    assert UsdPhysics.MassAPI(g).GetMassAttr().Get() == pytest.approx(sat, rel=1e-6)


def test_usd_without_moisture_has_dry_mass(tmp_path):
    scene = generate_scene("crushed_gravel", **SMALL)
    folder = write_outputs(scene, tmp_path)
    stage = Usd.Stage.Open(str(folder / "granulat_crushed_gravel.usdc"))
    prim = stage.GetPrimAtPath("/World/Grains").GetChildren()[0]
    assert not prim.GetVariantSets().HasVariantSet("moisture")
    expected = scene.prototypes[scene.instances[0]["proto"]]["mass"]
    assert UsdPhysics.MassAPI(prim).GetMassAttr().Get() == pytest.approx(expected, rel=1e-6)
    summary = json.loads((folder / "summary.json").read_text())
    assert summary["grains"] == 12 and summary["preset"] == "crushed_gravel"
