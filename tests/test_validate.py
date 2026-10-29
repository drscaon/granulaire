"""Every generated file passes OpenUSD's own validators (what usdchecker runs)."""

import pytest

from granulaire import Variations, generate_scene, write_outputs
from granulaire.validate import main, validate

PRESETS = ["crushed_gravel", "beach_sand", "wheat", "cherry_tomatoes", "packing_peanuts"]


@pytest.mark.parametrize("preset", PRESETS)
def test_openusd_validators(preset, tmp_path):
    # moisture on: every state of the moisture variant set is checked (ignored by presets without it)
    scene = generate_scene(preset, shapes=3, copies=2, variations=Variations(moisture=True))
    folder = write_outputs(scene, tmp_path)
    assert validate(folder / f"granulaire_{preset}.usdc") == []


def test_command_line(tmp_path, capsys):
    write_outputs(generate_scene("rounded_gravel", shapes=2, copies=1), tmp_path)
    assert main([str(tmp_path)]) == 0
    assert "0 with issues" in capsys.readouterr().out
