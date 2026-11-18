"""Every physical value names its source, and lies in the range its source gives (PRV-33).

docs/sources.md is written from granulaire.sources; this test fails on a value of the catalogue with no
source, on a source that is neither cited nor an explained estimate, on a value outside the range its
source gives, and when the page is not the module's tables.
"""

from pathlib import Path

import pytest

from granulaire import moisture, sources
from granulaire.presets import PRESETS

DOC = Path(__file__).parents[1] / "docs" / "sources.md"
BY_PATH = {v.path: v for v in sources.values()}


def test_every_number_of_the_catalogue_names_its_source():
    expected = ["moisture.POROSITY", "moisture.COHESION_REF_D"]
    for state in moisture.STATE_PARAMS:
        expected += [
            f"moisture.STATE_PARAMS.{state}.{f}" for f in ("film", "sat", "fill", "mu", "e", "cohesion")
        ]
    for key, p in PRESETS.items():
        for field in sources.PHYSICAL:
            if field in p:
                expected.append(f"PRESETS.{key}.{field}")
        for field in sources.SHAPE:
            if field in p:
                expected += [path for path, _ in sources._numbers(f"PRESETS.{key}.{field}", p[field])]
        for field in p.get("deformable", {}):
            if field != "tet_resolution":
                expected.append(f"PRESETS.{key}.deformable.{field}")
        known = (*sources.PHYSICAL, *sources.SHAPE, "deformable")
        ignored = ("subdivisions", "surface_roughness", "minerals", "curves", "dent_dir", "chip_axis")
        numeric = [f for f, x in p.items() if isinstance(x, (int, float, tuple)) and not isinstance(x, bool)]
        assert set(numeric) <= set(known) | set(ignored), (key, set(numeric) - set(known) - set(ignored))
    missing = [path for path in expected if path not in BY_PATH]
    assert not missing, f"no source for {missing}"


def test_values_are_the_code_values():
    for key, p in PRESETS.items():
        assert BY_PATH[f"PRESETS.{key}.density"].value == p["density"]
        assert BY_PATH[f"PRESETS.{key}.friction"].value == p["friction"]


@pytest.mark.parametrize("key", list(sources.SOURCES))
def test_a_source_is_cited_or_an_explained_estimate(key):
    s = sources.SOURCES[key]
    assert s.kind in sources.KINDS
    if s.kind == "estimate":
        assert s.note, f"{key}: an estimate says what it rests on"
    else:
        assert s.urls and all(u.startswith("https://") for u in s.urls), f"{key}: where to read it"


def test_every_source_is_used():
    used = {v.source for v in sources.values()}
    assert set(sources.SOURCES) == used, set(sources.SOURCES) - used


def test_every_value_lies_in_the_range_its_source_gives():
    for v in sources.values():
        assert v.source in sources.SOURCES, v.path
        if v.low is not None:
            assert v.value >= v.low - 1e-9, v.path
        if v.high is not None:
            assert v.value <= v.high + 1e-9, v.path


def test_documentation_is_the_sources():
    text = DOC.read_text(encoding="utf-8")
    start, end = "<!-- sources: begin -->\n", "<!-- sources: end -->"
    assert start in text and end in text
    written = text[text.index(start) + len(start) : text.index(end)]
    assert written.strip() == sources.table().strip(), "docs/sources.md: run python -m granulaire.sources"
