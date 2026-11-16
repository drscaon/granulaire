"""Every grain draws what docs/variation.md declares (PRV-34).

For every preset, thousands of grains are drawn with fixed seeds (the draws only, not the
geometry), so the result is the same on every run. Every value must lie in its declared range
and follow its rule (chi-square for choices and whole numbers, Kolmogorov-Smirnov for the rest, at
p > 0.001), and a grain must record exactly the values its body uses. The rules are in
granulaire.declared, which also writes the documentation. The grading of the sizes is tested
further in tests/test_grading.py.
"""

from pathlib import Path

import numpy as np
import pytest
from scipy import stats

from granulaire import declared
from granulaire.generator import Variations, sample_color, sample_params
from granulaire.presets import PRESETS
from granulaire.usd_export import drawn_values

N = 2000
P_MIN = 1e-3
DOC = Path(__file__).parents[1] / "docs" / "variation.md"


def draws(key):
    rng = np.random.default_rng(20261116)
    rows = []
    for _ in range(N):  # in the generator's order: the shape parameters, then the colour
        params = sample_params(rng, PRESETS[key], Variations())
        mineral, color = sample_color(rng, PRESETS[key], Variations())
        rows.append(drawn_values({"params": params, "mineral": mineral, "color": color}))
    return rows


def pair(p, name):
    v = p.get(name)
    return (0, 0) if v is None else v


def chi2_integers(values, lo, hi, what):
    expected = {k: 1.0 for k in range(int(lo), int(hi) + 1)}
    observed = np.array([np.sum(values == k) for k in expected])
    assert observed.sum() == len(values), f"{what}: a value outside {lo} to {hi}"
    if len(expected) > 1:
        assert stats.chisquare(observed).pvalue > P_MIN, f"{what}: {observed}"


def ks(values, cdf, what):
    assert stats.kstest(values, cdf).pvalue > P_MIN, what


@pytest.mark.parametrize("key", list(PRESETS))
def test_drawn_as_declared(key):
    p, rows = PRESETS[key], draws(key)
    expected = set(declared.columns(p))
    for row in rows[:5]:
        assert set(row) == expected, f"{key}: records {sorted(row)}, its body uses {sorted(expected)}"
    for name, _aspect, rule, bodies in declared.DECLARED:
        if declared.body(p) not in bodies:
            continue
        kind, *args = rule
        what = f"{key}: {name}"
        if name == "color_rgb":
            continue  # with the mineral, below
        values = np.array([row[name] for row in rows], dtype=object if name == "mineral" else float)
        if kind == "normal":
            ks(values, stats.norm(p[args[0]], p[args[1]]).cdf, what)
        elif kind == "diameter":
            phi = np.array([row["phi"] for row in rows])
            assert np.allclose(values, 2.0**-phi / 1000.0), what
        elif kind == "beta_min":
            a, b = p[args[0]]
            floor = p.get(args[1], args[2])
            assert values.min() >= floor - 1e-12, f"{what}: below {floor}"
            inner = values[values > floor + 1e-12]
            dist = stats.beta(a, b)
            ks(inner, lambda x, d=dist, f=floor: (d.cdf(x) - d.cdf(f)) / d.sf(f), what)
            raised, share = len(values) - len(inner), dist.cdf(floor) * len(values)
            assert abs(raised - share) < 3.5 * np.sqrt(share) + 1, f"{what}: {raised} raised to {floor}"
        elif kind in ("uniform", "taper"):
            v = p.get("taper", 0.0) if kind == "taper" else pair(p, args[0])
            lo, hi = v if isinstance(v, tuple) else (-v, v)
            assert lo - 1e-12 <= values.min() and values.max() <= hi + 1e-12, f"{what}: outside {lo} to {hi}"
            if hi > lo:
                ks(values, stats.uniform(lo, hi - lo).cdf, what)
        elif kind == "integers":
            chi2_integers(values, *pair(p, args[0]), what)
        elif kind == "loguniform":
            lo, hi = p[args[0]]
            assert lo - 1e-9 <= values.min() and values.max() <= hi + 1e-9, what
            if hi > lo:
                ks(np.log(values), stats.uniform(np.log(lo), np.log(hi / lo)).cdf, what)
        elif kind == "weights":
            names = [m[0] for m in p["minerals"]]
            weights = np.array([m[1] for m in p["minerals"]], float)
            observed = np.array([np.sum(values == n) for n in names])
            assert observed.sum() == len(values), f"{what}: a mineral outside {names}"
            assert stats.chisquare(observed, weights / weights.sum() * len(values)).pvalue > P_MIN, what
            # the tint: each channel of the colour is the mineral's, × 0.88 to 1.12, + noise sd 0.02
            base = {m[0]: np.array(m[2]) for m in p["minerals"]}
            for row in rows:
                c, b = np.array(row["color_rgb"]), base[row["mineral"]]
                low, high = np.clip(b * 0.88 - 0.1, 0, 1), np.clip(b * 1.12 + 0.1, 0, 1)
                assert np.all(c >= low - 1e-9) and np.all(c <= high + 1e-9), f"{key}: colour {c} for {b}"


def test_documentation_is_the_declaration():
    text = DOC.read_text(encoding="utf-8")
    begin, end = "<!-- declared: begin -->\n", "<!-- declared: end -->"
    assert begin in text and end in text, "docs/variation.md has lost its markers"
    block = text[text.index(begin) + len(begin) : text.index(end)].strip()
    assert block == declared.table().strip(), (
        "docs/variation.md is out of date: python -m granulaire.declared"
    )
