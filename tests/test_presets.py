import pytest

from granulat.presets import CATEGORIES, PRESETS

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
