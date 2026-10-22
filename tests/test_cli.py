import json

import pytest

from granulat import __version__
from granulat.cli import main


def test_list(capsys):
    assert main(["list"]) == 0
    out = capsys.readouterr().out
    assert "beach_sand" in out and "Reference" in out


def test_version(capsys):
    with pytest.raises(SystemExit):
        main(["--version"])
    assert __version__ in capsys.readouterr().out


def test_generate_with_toggles(tmp_path, capsys):
    code = main(
        [
            "generate",
            "--preset",
            "rounded_gravel",
            "--shapes",
            "4",
            "--copies",
            "1",
            "--no-size",
            "--moisture",
            "--moisture-weights",
            "0,0,1,0",
            "--out",
            str(tmp_path),
        ]
    )
    assert code == 0
    summary = json.loads((tmp_path / "rounded_gravel" / "summary.json").read_text())
    assert summary["variations"]["size"] is False
    assert summary["moisture"]["grains_per_state"]["wet"] == 4


def test_render(tmp_path):
    pytest.importorskip("matplotlib")
    main(
        [
            "generate",
            "--preset",
            "beach_sand",
            "--shapes",
            "3",
            "--copies",
            "1",
            "--moisture",
            "--out",
            str(tmp_path),
        ]
    )
    folder = tmp_path / "beach_sand"
    assert main(["render", str(folder)]) == 0
    assert main(["render-moisture", str(folder)]) == 0
    for name in ("shape_sheet.png", "mix_preview.png"):
        assert (folder / name).stat().st_size > 0
    assert (tmp_path / "moisture_states.png").stat().st_size > 0
    gallery = tmp_path / "gallery.png"
    assert main(["render-gallery", str(folder), "--grains", "2", "--output", str(gallery)]) == 0
    assert gallery.stat().st_size > 0
