"""The sizes that are generated follow the preset's grading curve."""

import numpy as np
import pytest
from scipy import stats

from granulaire import Variations, generate_scene
from granulaire.generator import grading, sample_params, summarize
from granulaire.presets import PRESETS

DRAWS = 2000


@pytest.mark.parametrize("key", sorted(PRESETS))
def test_drawn_sizes_follow_the_grading_curve(key):
    """2000 draws per preset against the target normal law in phi units."""
    preset = PRESETS[key]
    rng = np.random.default_rng(20261113)
    d = np.array([sample_params(rng, preset, Variations())["diameter_m"] for _ in range(DRAWS)])
    phi = -np.log2(d * 1000.0)
    test = stats.kstest(phi, stats.norm(preset["phi_mean"], preset["phi_std"]).cdf)
    assert test.pvalue > 0.01, f"{key}: KS statistic {test.statistic:.3f}, p = {test.pvalue:.4f}"
    assert np.median(d) * 1000 == pytest.approx(2.0 ** -preset["phi_mean"], rel=0.05)


@pytest.mark.parametrize("key", sorted(PRESETS))
def test_each_grain_has_the_size_that_was_drawn(key):
    """The mesh is scaled so that its equal-volume diameter is the draw."""
    scene = generate_scene(key, shapes=3, copies=1, seed=3, deformable=False)
    for proto in scene.prototypes:
        assert proto["metrics"]["diameter_nominal_m"] == pytest.approx(
            proto["params"]["diameter_m"], rel=1e-3
        )


def test_summary_reports_the_grading():
    scene = generate_scene("crushed_gravel", shapes=12, copies=1, seed=1)
    curve = summarize(scene)["grading"]
    assert curve == grading(scene)
    assert curve["shapes"] == 12
    assert curve["target_d50_mm"] == pytest.approx(8.0)
    assert 0.0 <= curve["ks_statistic"] <= 1.0 and 0.0 <= curve["ks_pvalue"] <= 1.0


def test_no_grading_when_sizes_are_not_drawn():
    scene = generate_scene("crushed_gravel", shapes=3, copies=1, seed=1, variations=Variations(size=False))
    assert grading(scene) is None
    assert "grading" not in summarize(scene)
