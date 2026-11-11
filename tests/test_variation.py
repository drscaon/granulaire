"""What was drawn for each grain is written into the file (primvaria:variation:*)."""

from pxr import Usd

from granulaire import Variations, generate_scene, write_outputs
from granulaire.contract import asset_roots, variation


def _drawn(tmp_path, **variations):
    scene = generate_scene("crushed_gravel", shapes=4, copies=2, seed=5, variations=Variations(**variations))
    folder = write_outputs(scene, tmp_path)
    stage = Usd.Stage.Open(str(folder / "granulaire_crushed_gravel.usdc"))
    return scene, [variation(prim) for prim in asset_roots(stage)]


def test_every_grain_carries_its_draws(tmp_path):
    scene, drawn = _drawn(tmp_path, moisture=True)
    assert len(drawn) == len(scene.instances)
    for inst, d in zip(scene.instances, drawn, strict=True):
        proto = scene.prototypes[inst["proto"]]
        assert d["aspects"] == ["size", "shape", "roundness", "mineralogy", "orientation", "moisture"]
        assert d["diameter_m"] == proto["params"]["diameter_m"]
        assert d["facets"] == proto["params"]["facets"]
        assert d["mineral"] == proto["mineral"]
        assert d["moisture"] == inst["state"]


def test_an_aspect_switched_off_is_recorded_at_its_nominal_value(tmp_path):
    _, on = _drawn(tmp_path / "on")
    _, off = _drawn(tmp_path / "off", size=False)
    assert "size" not in off[0]["aspects"] and "moisture" not in off[0]["aspects"]
    assert len({d["diameter_m"] for d in off}) == 1 < len({d["diameter_m"] for d in on})
    # the other aspects keep their draws
    assert [d["elongation"] for d in off] == [d["elongation"] for d in on]
    assert [d["mineral"] for d in off] == [d["mineral"] for d in on]
