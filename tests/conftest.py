"""Fixtures shared by the tests."""

import pytest

from granulaire import Variations, generate_scene, write_outputs
from granulaire.contract import usd_files


@pytest.fixture(scope="session")
def contract_files(tmp_path_factory):
    """OpenUSD files freshly generated: rigid grains with moisture states, and deformable ones."""
    out = tmp_path_factory.mktemp("contract")
    for preset in ("crushed_gravel", "cherry_tomatoes"):
        write_outputs(generate_scene(preset, shapes=3, copies=2, variations=Variations(moisture=True)), out)
    return usd_files([out])
