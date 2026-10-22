import numpy as np
import pytest

from granulaire.presets import CATEGORIES, PRESETS

REQUIRED = {
    "category",
    "label",
    "phi_mean",
    "phi_std",
    "elongation_beta",
    "flatness_beta",
    "facets",
    "roundness_p",
    "roughness",
    "density",
    "friction",
    "restitution",
    "absorption",
    "subdivisions",
    "minerals",
}


@pytest.mark.parametrize("key", sorted(PRESETS))
def test_preset_is_complete(key):
    preset = PRESETS[key]
    assert REQUIRED <= preset.keys()
    assert preset["category"] in CATEGORIES
    assert preset["density"] > 0
    assert preset["facets"][0] <= preset["facets"][1]
    assert preset["roundness_p"][0] <= preset["roundness_p"][1]


@pytest.mark.parametrize("key", sorted(PRESETS))
def test_mineral_proportions_sum_to_one(key):
    total = sum(m[1] for m in PRESETS[key]["minerals"])
    assert total == pytest.approx(1.0)


def test_every_category_is_used():
    assert {p["category"] for p in PRESETS.values()} == set(CATEGORIES)


def test_material_families_have_distinct_shapes():
    from granulaire import generate_scene

    def mean_convexity(key):
        scene = generate_scene(key, shapes=8, copies=1, seed=3)
        return np.mean([p["metrics"]["convexity"] for p in scene.prototypes])

    assert mean_convexity("pozzolana") < mean_convexity("dune_sand") - 0.01


def test_beach_pebbles_are_flatter_and_river_pebbles_rounder():
    from granulaire import generate_scene

    def mean(key, metric):
        scene = generate_scene(key, shapes=12, copies=1, seed=4)
        return np.mean([p["metrics"][metric] for p in scene.prototypes])

    assert mean("beach_pebbles", "flatness_SI") < mean("river_pebbles", "flatness_SI") - 0.15
    assert mean("river_pebbles", "sphericity") > mean("beach_pebbles", "sphericity") + 0.1


def test_beach_pebbles_are_dark_basalt_and_white_marble():
    names = {name for name, _, _ in PRESETS["beach_pebbles"]["minerals"]}
    assert any("basalt" in n for n in names) and any("marble" in n for n in names)


def test_readme_friction_table_matches_presets():
    """The README friction table is written by hand: keep it in sync with the code."""
    import re
    from pathlib import Path

    from granulaire.moisture import STATE_PARAMS

    readme = (Path(__file__).parents[1] / "README.md").read_text(encoding="utf-8")
    rows = dict(re.findall(r"^\| `(\w+)` \| (\d\.\d\d \|.*)\|$", readme, re.M))
    for key, preset in PRESETS.items():
        cells = [c.strip() for c in rows[key].split("|")]
        mu, e = preset.get("friction", 0.6), preset.get("restitution", 0.1)
        expected = [f"{mu:.2f}", f"{mu * 0.9:.2f}", f"{e:.2f}"]
        if preset.get("moisture", True):
            expected += [f"{mu * STATE_PARAMS[s]['mu']:.2f}" for s in ("damp", "wet", "saturated")]
        else:
            expected += ["—"] * 3
        assert cells == expected, key
