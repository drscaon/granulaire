import pytest

from granulaire import moisture
from granulaire.moisture import STATES, cohesion, parse_weights, water_mass

# a 0.35 mm quartz sand grain and an 8 mm gravel grain (sphere approximation)
SAND = {"dry_mass": 2650 * 3.1416 * 0.35e-3**3 / 6, "area": 3.1416 * 0.35e-3**2}
GRAVEL = {"dry_mass": 2700 * 3.1416 * 8e-3**3 / 6, "area": 3.1416 * 8e-3**2}


def _content(grain, state, absorption=0.005, density=2650.0):
    return water_mass(state, grain["dry_mass"], grain["area"], absorption, density) / grain["dry_mass"]


def test_water_increases_from_dry_to_saturated():
    contents = [_content(SAND, s) for s in STATES]
    assert contents[0] == 0.0
    assert contents == sorted(contents)


def test_sand_holds_more_water_than_gravel():
    assert _content(SAND, "wet") > 5 * _content(GRAVEL, "wet", absorption=0.01, density=2700.0)


def test_film_is_capped_by_heap_porosity():
    w_max = moisture.POROSITY / (1 - moisture.POROSITY) * moisture.RHO_WATER / 2650.0
    tiny = {"dry_mass": 2650 * 3.1416 * 0.05e-3**3 / 6, "area": 3.1416 * 0.05e-3**2}
    assert _content(tiny, "saturated", absorption=0.0) == pytest.approx(w_max)


def test_cohesion_peaks_when_damp_and_shrinks_with_size():
    assert cohesion("dry", 0.35e-3) == 0.0
    assert cohesion("saturated", 0.35e-3) == 0.0
    assert cohesion("damp", 0.35e-3) > cohesion("wet", 0.35e-3) > 0
    assert cohesion("damp", 8e-3) < cohesion("damp", 0.35e-3)


def test_parse_weights_normalises():
    w = parse_weights("2,1,1,0")
    assert w == {"dry": 0.5, "damp": 0.25, "wet": 0.25, "saturated": 0.0}


@pytest.mark.parametrize("text", ["1,2,3", "0,0,0,0", "1,-1,1,1"])
def test_parse_weights_rejects_bad_input(text):
    with pytest.raises(ValueError):
        parse_weights(text)


def test_wet_colour_is_darker():
    dry, wet = moisture.wet_color((0.8, 0.7, 0.5), "dry"), moisture.wet_color((0.8, 0.7, 0.5), "wet")
    assert sum(wet) < sum(dry)
